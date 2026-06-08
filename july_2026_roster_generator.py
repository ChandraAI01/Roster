"""
Advanced Monthly Roster Generator for July 2026
Generates comprehensive shift schedules with all resource constraints
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Tuple, Set

class MonthlyRosterGenerator:
    """Generates optimized monthly rosters meeting all constraints"""
    
    DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    MONTH_DAYS = 31
    
    def __init__(self, resources: List[Dict]):
        """
        Initialize roster generator with resources
        
        Args:
            resources: List of resource dicts with:
                      - name, enterprise_id, career_level, level
        """
        self.resources = resources
        self.l1_5_resources = [r for r in resources if r['level'] == 'L1.5']
        self.l2_resources = [r for r in resources if r['level'] == 'L2']
        self.l3_resources = [r for r in resources if r['level'] == 'L3']
        self.ad_resources = [r for r in resources if r['level'] == 'AD']
        
    def get_day_of_week(self, day: int) -> str:
        """Get day name for July day (1-31)"""
        date_obj = datetime(2026, 7, day)
        return self.DAYS_OF_WEEK[date_obj.weekday()]
    
    def get_weekends(self) -> List[int]:
        """Get all weekend days (Saturdays and Sundays) in July"""
        weekends = []
        for day in range(1, self.MONTH_DAYS + 1):
            day_name = self.get_day_of_week(day)
            if day_name in ['Saturday', 'Sunday']:
                weekends.append(day)
        return weekends
    
    def assign_shifts_by_level(self) -> Dict[str, str]:
        """Assign shifts to resources based on level"""
        assignments = {}
        
        # L1.5: Distribute evenly across A, B, C
        for idx, resource in enumerate(self.l1_5_resources):
            shift = ['A', 'B', 'C'][idx % 3]
            assignments[resource['name']] = shift
        
        # L2: Distribute evenly across A, B
        for idx, resource in enumerate(self.l2_resources):
            shift = ['A', 'B'][idx % 2]
            assignments[resource['name']] = shift
        
        # L3 & AD: Always G
        for resource in self.l3_resources + self.ad_resources:
            assignments[resource['name']] = 'G'
        
        return assignments
    
    def generate_l1_5_rotated_weekoffs(self) -> Dict[str, List[int]]:
        """
        Generate rotated 2-day consecutive week-offs for L1.5 team
        Ensures each person gets different days off throughout the month
        """
        week_offs = {}
        
        # Define rotation patterns for 2-day consecutive offs
        # Each pattern represents (start_day_index_in_week, days_off_count)
        patterns = [
            (0, 2),   # Mon-Tue
            (1, 2),   # Tue-Wed
            (2, 2),   # Wed-Thu
            (3, 2),   # Thu-Fri
            (4, 2),   # Fri-Sat
            (5, 2),   # Sat-Sun
            (6, 2),   # Sun-Mon (wraps)
        ]
        
        for res_idx, resource in enumerate(self.l1_5_resources):
            res_offs = []
            
            # Generate week-offs for 4 weeks in July
            for week_num in range(1, 5):
                # Rotate pattern for each week
                pattern_idx = (res_idx + week_num) % len(patterns)
                start_day_in_week, num_days = patterns[pattern_idx]
                
                # Calculate actual calendar dates
                week_start_date = (week_num - 1) * 7 + 1
                
                for offset in range(num_days):
                    day_in_week = (start_day_in_week + offset) % 7
                    calendar_date = week_start_date + day_in_week
                    
                    if calendar_date <= self.MONTH_DAYS:
                        res_offs.append(calendar_date)
            
            week_offs[resource['name']] = res_offs
        
        return week_offs
    
    def generate_l2_weekend_oncall_rotation(self) -> Dict[int, Dict]:
        """
        Generate OP/OS rotation for L2 resources on every weekend
        Ensures fair distribution and no overlaps
        """
        oncall_assignments = {}
        weekends = self.get_weekends()
        num_l2 = len(self.l2_resources)
        
        for idx, day in enumerate(weekends):
            # Rotate OP and OS assignments fairly
            op_resource_idx = idx % num_l2
            os_resource_idx = (idx + 1) % num_l2
            
            oncall_assignments[day] = {
                'OP': self.l2_resources[op_resource_idx]['name'],
                'OS': self.l2_resources[os_resource_idx]['name']
            }
        
        return oncall_assignments
    
    def validate_weekend_l1_5_coverage(self, 
                                       shift_assignments: Dict[str, str],
                                       l1_5_weekoffs: Dict[str, List[int]]) -> bool:
        """
        Validate that minimum L1.5 coverage exists on weekends
        Minimum: 1 resource per shift (A, B, C)
        """
        weekends = self.get_weekends()
        
        for day in weekends:
            coverage = {'A': 0, 'B': 0, 'C': 0}
            
            for resource in self.l1_5_resources:
                if day not in l1_5_weekoffs[resource['name']]:
                    shift = shift_assignments[resource['name']]
                    coverage[shift] += 1
            
            # Check if all shifts have coverage
            if coverage['A'] == 0 or coverage['B'] == 0 or coverage['C'] == 0:
                print(f"Warning: Insufficient coverage on day {day}: {coverage}")
                return False
        
        return True
    
    def generate_monthly_roster(self) -> Dict:
        """Generate complete monthly roster for July 2026"""
        
        # Step 1: Assign shifts
        shift_assignments = self.assign_shifts_by_level()
        
        # Step 2: Generate L1.5 week-offs
        l1_5_weekoffs = self.generate_l1_5_rotated_weekoffs()
        
        # Step 3: Generate L2 weekend on-call
        l2_oncall = self.generate_l2_weekend_oncall_rotation()
        
        # Step 4: Validate weekend coverage
        coverage_valid = self.validate_weekend_l1_5_coverage(shift_assignments, l1_5_weekoffs)
        
        # Build roster
        roster = {
            'month': 'July',
            'year': 2026,
            'coverage_valid': coverage_valid,
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'daily_schedule': {}
        }
        
        # Generate daily assignments for each resource
        for resource in self.resources:
            daily_schedule = {}
            shift = shift_assignments[resource['name']]
            
            for day in range(1, self.MONTH_DAYS + 1):
                day_name = self.get_day_of_week(day)
                day_info = {
                    'day': day_name,
                    'date': f"Jul-{day}",
                    'assignment': ''
                }
                
                if resource['level'] in ['L2', 'L3', 'AD']:
                    # Mon-Fri: Shift, Sat-Sun: WO
                    if day_name in ['Saturday', 'Sunday']:
                        day_info['assignment'] = 'WO'
                    else:
                        day_info['assignment'] = shift
                        
                else:  # L1.5
                    # Check if day is in week-offs
                    if day in l1_5_weekoffs[resource['name']]:
                        day_info['assignment'] = 'WO'
                    else:
                        day_info['assignment'] = shift
                
                daily_schedule[day] = day_info
            
            # Add L2 on-call assignments
            oncall_info = {}
            if resource['level'] == 'L2':
                for day, oncall_data in l2_oncall.items():
                    if resource['name'] == oncall_data['OP']:
                        oncall_info[day] = 'OP'
                    elif resource['name'] == oncall_data['OS']:
                        oncall_info[day] = 'OS'
            
            roster[resource['name']] = {
                'enterprise_id': resource['enterprise_id'],
                'career_level': resource['career_level'],
                'level': resource['level'],
                'shift': shift,
                'daily_schedule': daily_schedule,
                'oncall_days': oncall_info if oncall_info else None
            }
        
        return roster
    
    def export_to_csv(self, roster: Dict) -> str:
        """Export roster to CSV format"""
        lines = []
        
        # Header: Resource Name, Enterprise ID, Level, Shift, then all days
        header = "Resource Name,Enterprise ID,Career Level,Level,Shift,"
        for day in range(1, self.MONTH_DAYS + 1):
            day_name = self.get_day_of_week(day)
            header += f"Jul-{day}({day_name[:3]}),"
        header = header.rstrip(',')
        lines.append(header)
        
        # Data rows
        resource_names = [r['name'] for r in self.resources]
        for name in resource_names:
            if name not in roster:
                continue
                
            res_data = roster[name]
            row = [
                name,
                res_data['enterprise_id'],
                res_data['career_level'],
                res_data['level'],
                res_data['shift']
            ]
            
            # Add daily assignments
            for day in range(1, self.MONTH_DAYS + 1):
                assignment = res_data['daily_schedule'][day]['assignment']
                
                # Add OP/OS designation for L2 resources
                if res_data['level'] == 'L2' and day in (res_data.get('oncall_days') or {}):
                    assignment += f"({res_data['oncall_days'][day]})"
                
                row.append(assignment)
            
            lines.append(','.join(row))
        
        return '\n'.join(lines)
    
    def generate_summary_report(self, roster: Dict) -> str:
        """Generate summary statistics and validation report"""
        report = []
        report.append("=" * 100)
        report.append("JULY 2026 MONTHLY ROSTER - SUMMARY REPORT")
        report.append("=" * 100)
        
        report.append("\n[1] RESOURCE DISTRIBUTION BY LEVEL")
        report.append("-" * 100)
        report.append(f"  L1.5 Resources: {len(self.l1_5_resources)}")
        
        shift_count_l1_5 = {'A': 0, 'B': 0, 'C': 0}
        for res in self.l1_5_resources:
            if res['name'] in roster:
                shift = roster[res['name']]['shift']
                shift_count_l1_5[shift] += 1
        
        report.append(f"    • Shift A: {shift_count_l1_5['A']}")
        report.append(f"    • Shift B: {shift_count_l1_5['B']}")
        report.append(f"    • Shift C: {shift_count_l1_5['C']}")
        
        report.append(f"\n  L2 Resources: {len(self.l2_resources)}")
        shift_count_l2 = {'A': 0, 'B': 0}
        for res in self.l2_resources:
            if res['name'] in roster:
                shift = roster[res['name']]['shift']
                shift_count_l2[shift] += 1
        
        report.append(f"    • Shift A: {shift_count_l2['A']}")
        report.append(f"    • Shift B: {shift_count_l2['B']}")
        
        report.append(f"\n  L3 Resources: {len(self.l3_resources)} (All in G Shift)")
        report.append(f"  AD Resources: {len(self.ad_resources)} (All in G Shift)")
        
        report.append("\n[2] L1.5 WEEK-OFF ROTATION")
        report.append("-" * 100)
        for res in self.l1_5_resources:
            if res['name'] in roster:
                days_off = []
                for day in range(1, self.MONTH_DAYS + 1):
                    if roster[res['name']]['daily_schedule'][day]['assignment'] == 'WO':
                        days_off.append(f"Jul-{day}")
                report.append(f"  {res['name']}: {', '.join(days_off)}")
        
        report.append("\n[3] L2 WEEKEND ON-CALL ROTATION")
        report.append("-" * 100)
        for res in self.l2_resources:
            if res['name'] in roster and roster[res['name']].get('oncall_days'):
                oncall_days = roster[res['name']]['oncall_days']
                oncall_str = ', '.join([f"Jul-{day}({role})" for day, role in sorted(oncall_days.items())])
                report.append(f"  {res['name']}: {oncall_str}")
        
        report.append("\n[4] VALIDATION STATUS")
        report.append("-" * 100)
        report.append(f"  Weekend Coverage Valid: {'✓ PASS' if roster['coverage_valid'] else '✗ FAIL'}")
        report.append(f"  Generated: {roster['generated_at']}")
        
        report.append("\n" + "=" * 100)
        
        return '\n'.join(report)
    
    def export_json(self, roster: Dict) -> str:
        """Export roster as JSON"""
        return json.dumps(roster, indent=2)


# Example Usage
if __name__ == "__main__":
    resources = [
        {'name': 'Bhagya Lakshmi', 'enterprise_id': 'p.a.bhagya.lakshmi', 'career_level': '12', 'level': 'L1.5'},
        {'name': 'Jerin Victoria', 'enterprise_id': 'jerin.darwin.joseph', 'career_level': '12', 'level': 'L1.5'},
        {'name': 'Prasanna Lakshmi', 'enterprise_id': 'k.b.prasanna.lakshmi', 'career_level': '12', 'level': 'L1.5'},
        {'name': 'Sahithi Kappa', 'enterprise_id': 'Kapa.sahithi', 'career_level': '12', 'level': 'L1.5'},
        {'name': 'Mathav Thirumalsamy', 'enterprise_id': 'mathav.thirumalsamy', 'career_level': '12', 'level': 'L1.5'},
        {'name': 'Sai Priya Kota', 'enterprise_id': 'kota.sai.priya', 'career_level': '12', 'level': 'L1.5'},
        {'name': 'Nirmal Kumar', 'enterprise_id': 'nirmal.b.kumar.s', 'career_level': '11', 'level': 'L2'},
        {'name': 'Ankita Bidwai', 'enterprise_id': 'ankita.bidwai', 'career_level': '11', 'level': 'L2'},
        {'name': 'Maruti Mane', 'enterprise_id': 'maruti.babruvan.mane', 'career_level': '10', 'level': 'L2'},
        {'name': 'Omkar Kale', 'enterprise_id': 'omkar.b.kale', 'career_level': '10', 'level': 'L2'},
        {'name': 'Singaram CT', 'enterprise_id': 'singaram.ct', 'career_level': '10', 'level': 'L2'},
        {'name': 'Rohit Pawar', 'enterprise_id': 'rohit.pralhad.pawar', 'career_level': '10', 'level': 'L2'},
        {'name': 'Chandra Shekhar Yadav', 'enterprise_id': 'c.shekhar.yadav', 'career_level': '9', 'level': 'AD'},
        {'name': 'Suraj Narang', 'enterprise_id': 'suraj.narang', 'career_level': '8', 'level': 'L3'},
        {'name': 'Vikram Kumar', 'enterprise_id': 'k.vikram', 'career_level': '8', 'level': 'L3'},
        {'name': 'Brijesh Agrawal', 'enterprise_id': 'brijesh.agrawal', 'career_level': '6', 'level': 'L3'},
    ]
    
    generator = MonthlyRosterGenerator(resources)
    roster = generator.generate_monthly_roster()
    
    # Export as CSV
    print(generator.export_to_csv(roster))
    
    # Print summary report
    print("\n" + generator.generate_summary_report(roster))
