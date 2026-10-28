from neo4j import Session
from typing import Dict, Any
import logging

logger = logging.getLogger("unienroll.seed")

class SeedService:
    @staticmethod
    def reset_and_seed(session: Session) -> Dict[str, Any]:
        """
        Clears existing UniEnroll data, sets constraints, and populates full VIT Chennai FFCS data.
        """
        logger.info("Resetting and seeding database...")

        # 1. Clear existing nodes and relationships
        session.run("MATCH (n) DETACH DELETE n")

        # 2. Create constraints
        constraints = [
            "CREATE CONSTRAINT student_reg_no_unique IF NOT EXISTS FOR (s:Student) REQUIRE s.reg_no IS UNIQUE",
            "CREATE CONSTRAINT faculty_id_unique IF NOT EXISTS FOR (f:Faculty) REQUIRE f.faculty_id IS UNIQUE",
            "CREATE CONSTRAINT course_code_unique IF NOT EXISTS FOR (c:Course) REQUIRE c.course_code IS UNIQUE",
            "CREATE CONSTRAINT slot_name_unique IF NOT EXISTS FOR (sl:Slot) REQUIRE sl.slot_name IS UNIQUE",
            "CREATE CONSTRAINT class_id_unique IF NOT EXISTS FOR (cl:Class) REQUIRE cl.class_id IS UNIQUE"
        ]
        for c in constraints:
            try:
                session.run(c)
            except Exception as e:
                logger.warning(f"Constraint warning: {e}")

        # 3. Create Slots
        slots_cypher = """
        UNWIND [
            {slot_name: 'A1', day: 'MON', start_time: '08:00', end_time: '08:50'},
            {slot_name: 'B1', day: 'MON', start_time: '09:00', end_time: '09:50'},
            {slot_name: 'C1', day: 'TUE', start_time: '08:00', end_time: '08:50'},
            {slot_name: 'D1', day: 'WED', start_time: '10:00', end_time: '10:50'},
            {slot_name: 'E1', day: 'WED', start_time: '11:00', end_time: '11:50'},
            {slot_name: 'F1', day: 'THU', start_time: '10:00', end_time: '10:50'},
            {slot_name: 'G1', day: 'FRI', start_time: '11:00', end_time: '11:50'},
            {slot_name: 'TA1', day: 'TUE', start_time: '14:00', end_time: '14:50'},
            {slot_name: 'TB1', day: 'WED', start_time: '14:00', end_time: '14:50'},
            {slot_name: 'TC1', day: 'THU', start_time: '14:00', end_time: '14:50'},
            {slot_name: 'TD1', day: 'FRI', start_time: '14:00', end_time: '14:50'}
        ] AS s
        CREATE (:Slot {
            slot_name: s.slot_name,
            day: s.day,
            start_time: s.start_time,
            end_time: s.end_time
        })
        """
        session.run(slots_cypher)

        # 4. Create Venues (including a deliberately low capacity room to show overbooking)
        venues_cypher = """
        UNWIND [
            {building: 'AB1', room_no: '101', capacity: 60},
            {building: 'AB1', room_no: '102', capacity: 55},
            {building: 'AB1', room_no: '201', capacity: 3},
            {building: 'AB2', room_no: '201', capacity: 70},
            {building: 'AB3', room_no: '301', capacity: 45},
            {building: 'SMV', room_no: '101', capacity: 120},
            {building: 'SMV', room_no: '201', capacity: 60},
            {building: 'TT', room_no: '301', capacity: 50},
            {building: 'TT', room_no: '405', capacity: 65}
        ] AS v
        CREATE (:Venue {
            building: v.building,
            room_no: v.room_no,
            capacity: v.capacity
        })
        """
        session.run(venues_cypher)

        # 5. Create Faculty
        faculty_cypher = """
        UNWIND [
            {faculty_id: 'F_101', emp_id: 'F_101', name: 'Dr. Ramesh Kumar', designation: 'Professor', department: 'SCOPE', school: 'SCOPE'},
            {faculty_id: 'F_102', emp_id: 'F_102', name: 'Prof. Anjali Desai', designation: 'Associate Professor', department: 'SAS', school: 'SAS'},
            {faculty_id: 'F_103', emp_id: 'F_103', name: 'Dr. Suresh Verma', designation: 'Associate Professor', department: 'SAS', school: 'SAS'},
            {faculty_id: 'F_104', emp_id: 'F_104', name: 'Dr. Lakshmi Narayanan', designation: 'Professor', department: 'SCOPE', school: 'SCOPE'},
            {faculty_id: 'F_105', emp_id: 'F_105', name: 'Dr. Priya Swaminathan', designation: 'Assistant Professor', department: 'SENSE', school: 'SENSE'},
            {faculty_id: 'F_106', emp_id: 'F_106', name: 'Prof. Vikram Seth', designation: 'Assistant Professor', department: 'SCOPE', school: 'SCOPE'}
        ] AS f
        CREATE (:Faculty {
            faculty_id: f.faculty_id,
            emp_id: f.emp_id,
            name: f.name,
            designation: f.designation,
            department: f.department,
            school: f.school
        })
        """
        session.run(faculty_cypher)

        # 6. Create Courses
        courses_cypher = """
        UNWIND [
            {course_code: 'CSE1001', title: 'Problem Solving and Programming', credits: 4, department: 'SCOPE'},
            {course_code: 'CSE2001', title: 'Data Structures and Algorithms', credits: 4, department: 'SCOPE'},
            {course_code: 'CSE2004', title: 'Database Management Systems', credits: 4, department: 'SCOPE'},
            {course_code: 'CSE3001', title: 'Operating Systems', credits: 4, department: 'SCOPE'},
            {course_code: 'CSE3002', title: 'Computer Networks', credits: 3, department: 'SCOPE'},
            {course_code: 'MAT1011', title: 'Calculus for Engineers', credits: 3, department: 'SAS'},
            {course_code: 'MAT2001', title: 'Discrete Mathematics', credits: 3, department: 'SAS'},
            {course_code: 'PHY1001', title: 'Engineering Physics', credits: 3, department: 'SAS'},
            {course_code: 'ECE2002', title: 'Digital Logic Design', credits: 3, department: 'SENSE'}
        ] AS c
        CREATE (:Course {
            course_code: c.course_code,
            title: c.title,
            credits: c.credits,
            department: c.department
        })
        """
        session.run(courses_cypher)

        # 7. Create Classes and Relationships to Course, Slot, Venue, Faculty
        classes_cypher = """
        UNWIND [
            {class_id: '101', course: 'CSE1001', slot: 'A1', building: 'AB1', room: '101', faculty: 'Dr. Ramesh Kumar'},
            {class_id: '102', course: 'CSE1001', slot: 'B1', building: 'AB1', room: '102', faculty: 'Dr. Ramesh Kumar'},
            {class_id: '201', course: 'MAT1011', slot: 'A1', building: 'AB2', room: '201', faculty: 'Prof. Anjali Desai'},
            {class_id: '301', course: 'PHY1001', slot: 'C1', building: 'AB3', room: '301', faculty: 'Dr. Suresh Verma'},
            {class_id: '401', course: 'CSE2001', slot: 'D1', building: 'SMV', room: '101', faculty: 'Dr. Lakshmi Narayanan'},
            {class_id: '402', course: 'CSE2001', slot: 'E1', building: 'SMV', room: '201', faculty: 'Prof. Vikram Seth'},
            {class_id: '501', course: 'CSE2004', slot: 'B1', building: 'AB1', room: '201', faculty: 'Dr. Lakshmi Narayanan'},
            {class_id: '502', course: 'CSE3001', slot: 'F1', building: 'TT', room: '301', faculty: 'Prof. Vikram Seth'},
            {class_id: '503', course: 'CSE3002', slot: 'G1', building: 'TT', room: '405', faculty: 'Dr. Priya Swaminathan'},
            {class_id: '504', course: 'MAT2001', slot: 'TA1', building: 'AB1', room: '102', faculty: 'Prof. Anjali Desai'},
            {class_id: '505', course: 'ECE2002', slot: 'TB1', building: 'SMV', room: '201', faculty: 'Dr. Priya Swaminathan'}
        ] AS item
        CREATE (cl:Class {class_id: item.class_id})
        WITH cl, item
        MATCH (c:Course {course_code: item.course})
        MATCH (sl:Slot {slot_name: item.slot})
        MATCH (v:Venue {building: item.building, room_no: item.room})
        MATCH (f:Faculty {name: item.faculty})
        CREATE (cl)-[:FOR_COURSE]->(c)
        CREATE (cl)-[:SCHEDULED_AT]->(sl)
        CREATE (cl)-[:HELD_IN]->(v)
        CREATE (cl)-[:TAUGHT_BY]->(f)
        """
        session.run(classes_cypher)

        # 8. Create Students
        students_cypher = """
        UNWIND [
            {reg_no: '21BCE1001', name: 'Aarav Sharma', department: 'CSE', program: 'CSE'},
            {reg_no: '21BCE1002', name: 'Priya Patel', department: 'CSE', program: 'CSE'},
            {reg_no: '21BCE1003', name: 'Rohan Gupta', department: 'IT', program: 'IT'},
            {reg_no: '21BME2001', name: 'Sneha Reddy', department: 'MECH', program: 'MECH'},
            {reg_no: '21BCE1005', name: 'Karthik Raman', department: 'CSE', program: 'CSE'}
        ] AS s
        CREATE (:Student {
            reg_no: s.reg_no,
            name: s.name,
            department: s.department,
            program: s.program,
            total_credits: 0
        })
        """
        session.run(students_cypher)

        # 9. Register Students into Classes
        # Note: Rohan Gupta (21BCE1003) is intentionally registered in 101 AND 201, both scheduled at Slot A1!
        # Class 501 (AB1-201, capacity 3) has 4 registrations to trigger overbooking audit!
        registrations_cypher = """
        UNWIND [
            // Aarav Sharma (21BCE1001) - Clean registration
            {reg_no: '21BCE1001', class_id: '101'},
            {reg_no: '21BCE1001', class_id: '301'},
            {reg_no: '21BCE1001', class_id: '402'},
            {reg_no: '21BCE1001', class_id: '502'},

            // Priya Patel (21BCE1002) - Clean registration
            {reg_no: '21BCE1002', class_id: '102'},
            {reg_no: '21BCE1002', class_id: '401'},
            {reg_no: '21BCE1002', class_id: '503'},
            {reg_no: '21BCE1002', class_id: '504'},

            // Rohan Gupta (21BCE1003) - DELIBERATE CONFLICT: Class 101 and Class 201 are BOTH in Slot A1!
            {reg_no: '21BCE1003', class_id: '101'},
            {reg_no: '21BCE1003', class_id: '201'},
            {reg_no: '21BCE1003', class_id: '401'},

            // Sneha Reddy (21BME2001)
            {reg_no: '21BME2001', class_id: '301'},
            {reg_no: '21BME2001', class_id: '401'},

            // Registrations in Class 501 (Capacity = 3, Enrolled = 4 -> OVERBOOKED)
            {reg_no: '21BCE1001', class_id: '501'},
            {reg_no: '21BCE1002', class_id: '501'},
            {reg_no: '21BCE1003', class_id: '501'},
            {reg_no: '21BCE1005', class_id: '501'}
        ] AS reg
        MATCH (s:Student {reg_no: reg.reg_no})
        MATCH (cl:Class {class_id: reg.class_id})
        MERGE (s)-[:REGISTERED_IN]->(cl)
        """
        session.run(registrations_cypher)

        # 10. Update total credits on Student nodes
        update_credits_cypher = """
        MATCH (s:Student)
        OPTIONAL MATCH (s)-[:REGISTERED_IN]->(cl:Class)-[:FOR_COURSE]->(c:Course)
        WITH s, coalesce(sum(c.credits), 0) AS total
        SET s.total_credits = total
        """
        session.run(update_credits_cypher)

        return {
            "status": "success",
            "message": "VIT Chennai FFCS seed data populated successfully with intentional conflict test cases."
        }
