// ===================================================
// UniEnroll FFCS Management Platform - Seed Migration
// VIT Chennai Graph Schema & Seed Data
// ===================================================

// 1. Constraints
CREATE CONSTRAINT student_reg_no_unique IF NOT EXISTS FOR (s:Student) REQUIRE s.reg_no IS UNIQUE;
CREATE CONSTRAINT faculty_id_unique IF NOT EXISTS FOR (f:Faculty) REQUIRE f.faculty_id IS UNIQUE;
CREATE CONSTRAINT course_code_unique IF NOT EXISTS FOR (c:Course) REQUIRE c.course_code IS UNIQUE;
CREATE CONSTRAINT slot_name_unique IF NOT EXISTS FOR (sl:Slot) REQUIRE sl.slot_name IS UNIQUE;
CREATE CONSTRAINT class_id_unique IF NOT EXISTS FOR (cl:Class) REQUIRE cl.class_id IS UNIQUE;

// 2. Clear Database
MATCH (n) DETACH DELETE n;

// 3. Create Slots
CREATE (:Slot {slot_name: 'A1', day: 'MON', start_time: '08:00', end_time: '08:50'});
CREATE (:Slot {slot_name: 'B1', day: 'MON', start_time: '09:00', end_time: '09:50'});
CREATE (:Slot {slot_name: 'C1', day: 'TUE', start_time: '08:00', end_time: '08:50'});
CREATE (:Slot {slot_name: 'D1', day: 'WED', start_time: '10:00', end_time: '10:50'});
CREATE (:Slot {slot_name: 'E1', day: 'WED', start_time: '11:00', end_time: '11:50'});
CREATE (:Slot {slot_name: 'F1', day: 'THU', start_time: '10:00', end_time: '10:50'});
CREATE (:Slot {slot_name: 'G1', day: 'FRI', start_time: '11:00', end_time: '11:50'});
CREATE (:Slot {slot_name: 'TA1', day: 'TUE', start_time: '14:00', end_time: '14:50'});
CREATE (:Slot {slot_name: 'TB1', day: 'WED', start_time: '14:00', end_time: '14:50'});
CREATE (:Slot {slot_name: 'TC1', day: 'THU', start_time: '14:00', end_time: '14:50'});
CREATE (:Slot {slot_name: 'TD1', day: 'FRI', start_time: '14:00', end_time: '14:50'});

// 4. Create Venues
CREATE (:Venue {building: 'AB1', room_no: '101', capacity: 60});
CREATE (:Venue {building: 'AB1', room_no: '102', capacity: 55});
CREATE (:Venue {building: 'AB1', room_no: '201', capacity: 3});
CREATE (:Venue {building: 'AB2', room_no: '201', capacity: 70});
CREATE (:Venue {building: 'AB3', room_no: '301', capacity: 45});
CREATE (:Venue {building: 'SMV', room_no: '101', capacity: 120});
CREATE (:Venue {building: 'SMV', room_no: '201', capacity: 60});
CREATE (:Venue {building: 'TT', room_no: '301', capacity: 50});
CREATE (:Venue {building: 'TT', room_no: '405', capacity: 65});

// 5. Create Faculty
CREATE (:Faculty {faculty_id: 'F_101', emp_id: 'F_101', name: 'Dr. Ramesh Kumar', designation: 'Professor', department: 'SCOPE', school: 'SCOPE'});
CREATE (:Faculty {faculty_id: 'F_102', emp_id: 'F_102', name: 'Prof. Anjali Desai', designation: 'Associate Professor', department: 'SAS', school: 'SAS'});
CREATE (:Faculty {faculty_id: 'F_103', emp_id: 'F_103', name: 'Dr. Suresh Verma', designation: 'Associate Professor', department: 'SAS', school: 'SAS'});
CREATE (:Faculty {faculty_id: 'F_104', emp_id: 'F_104', name: 'Dr. Lakshmi Narayanan', designation: 'Professor', department: 'SCOPE', school: 'SCOPE'});
CREATE (:Faculty {faculty_id: 'F_105', emp_id: 'F_105', name: 'Dr. Priya Swaminathan', designation: 'Assistant Professor', department: 'SENSE', school: 'SENSE'});
CREATE (:Faculty {faculty_id: 'F_106', emp_id: 'F_106', name: 'Prof. Vikram Seth', designation: 'Assistant Professor', department: 'SCOPE', school: 'SCOPE'});

// 6. Create Courses
CREATE (:Course {course_code: 'CSE1001', title: 'Problem Solving and Programming', credits: 4, department: 'SCOPE'});
CREATE (:Course {course_code: 'CSE2001', title: 'Data Structures and Algorithms', credits: 4, department: 'SCOPE'});
CREATE (:Course {course_code: 'CSE2004', title: 'Database Management Systems', credits: 4, department: 'SCOPE'});
CREATE (:Course {course_code: 'CSE3001', title: 'Operating Systems', credits: 4, department: 'SCOPE'});
CREATE (:Course {course_code: 'CSE3002', title: 'Computer Networks', credits: 3, department: 'SCOPE'});
CREATE (:Course {course_code: 'MAT1011', title: 'Calculus for Engineers', credits: 3, department: 'SAS'});
CREATE (:Course {course_code: 'MAT2001', title: 'Discrete Mathematics', credits: 3, department: 'SAS'});
CREATE (:Course {course_code: 'PHY1001', title: 'Engineering Physics', credits: 3, department: 'SAS'});
CREATE (:Course {course_code: 'ECE2002', title: 'Digital Logic Design', credits: 3, department: 'SENSE'});

// 7. Create Classes and Relationships
MATCH (c:Course {course_code: 'CSE1001'}), (sl:Slot {slot_name: 'A1'}), (v:Venue {building: 'AB1', room_no: '101'}), (f:Faculty {name: 'Dr. Ramesh Kumar'})
CREATE (cl:Class {class_id: '101'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'CSE1001'}), (sl:Slot {slot_name: 'B1'}), (v:Venue {building: 'AB1', room_no: '102'}), (f:Faculty {name: 'Dr. Ramesh Kumar'})
CREATE (cl:Class {class_id: '102'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'MAT1011'}), (sl:Slot {slot_name: 'A1'}), (v:Venue {building: 'AB2', room_no: '201'}), (f:Faculty {name: 'Prof. Anjali Desai'})
CREATE (cl:Class {class_id: '201'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'PHY1001'}), (sl:Slot {slot_name: 'C1'}), (v:Venue {building: 'AB3', room_no: '301'}), (f:Faculty {name: 'Dr. Suresh Verma'})
CREATE (cl:Class {class_id: '301'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'CSE2001'}), (sl:Slot {slot_name: 'D1'}), (v:Venue {building: 'SMV', room_no: '101'}), (f:Faculty {name: 'Dr. Lakshmi Narayanan'})
CREATE (cl:Class {class_id: '401'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'CSE2001'}), (sl:Slot {slot_name: 'E1'}), (v:Venue {building: 'SMV', room_no: '201'}), (f:Faculty {name: 'Prof. Vikram Seth'})
CREATE (cl:Class {class_id: '402'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'CSE2004'}), (sl:Slot {slot_name: 'B1'}), (v:Venue {building: 'AB1', room_no: '201'}), (f:Faculty {name: 'Dr. Lakshmi Narayanan'})
CREATE (cl:Class {class_id: '501'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'CSE3001'}), (sl:Slot {slot_name: 'F1'}), (v:Venue {building: 'TT', room_no: '301'}), (f:Faculty {name: 'Prof. Vikram Seth'})
CREATE (cl:Class {class_id: '502'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'CSE3002'}), (sl:Slot {slot_name: 'G1'}), (v:Venue {building: 'TT', room_no: '405'}), (f:Faculty {name: 'Dr. Priya Swaminathan'})
CREATE (cl:Class {class_id: '503'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'MAT2001'}), (sl:Slot {slot_name: 'TA1'}), (v:Venue {building: 'AB1', room_no: '102'}), (f:Faculty {name: 'Prof. Anjali Desai'})
CREATE (cl:Class {class_id: '504'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

MATCH (c:Course {course_code: 'ECE2002'}), (sl:Slot {slot_name: 'TB1'}), (v:Venue {building: 'SMV', room_no: '201'}), (f:Faculty {name: 'Dr. Priya Swaminathan'})
CREATE (cl:Class {class_id: '505'})-[:FOR_COURSE]->(c), (cl)-[:SCHEDULED_AT]->(sl), (cl)-[:HELD_IN]->(v), (cl)-[:TAUGHT_BY]->(f);

// 8. Create Students
CREATE (:Student {reg_no: '21BCE1001', name: 'Aarav Sharma', department: 'CSE', program: 'CSE', total_credits: 15});
CREATE (:Student {reg_no: '21BCE1002', name: 'Priya Patel', department: 'CSE', program: 'CSE', total_credits: 14});
CREATE (:Student {reg_no: '21BCE1003', name: 'Rohan Gupta', department: 'IT', program: 'IT', total_credits: 11});
CREATE (:Student {reg_no: '21BME2001', name: 'Sneha Reddy', department: 'MECH', program: 'MECH', total_credits: 7});
CREATE (:Student {reg_no: '21BCE1005', name: 'Karthik Raman', department: 'CSE', program: 'CSE', total_credits: 19});

// 9. Register Students into Classes
// Aarav Sharma
MATCH (s:Student {reg_no: '21BCE1001'}), (cl:Class {class_id: '101'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1001'}), (cl:Class {class_id: '301'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1001'}), (cl:Class {class_id: '402'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1001'}), (cl:Class {class_id: '502'}) CREATE (s)-[:REGISTERED_IN]->(cl);

// Priya Patel
MATCH (s:Student {reg_no: '21BCE1002'}), (cl:Class {class_id: '102'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1002'}), (cl:Class {class_id: '401'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1002'}), (cl:Class {class_id: '503'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1002'}), (cl:Class {class_id: '504'}) CREATE (s)-[:REGISTERED_IN]->(cl);

// Rohan Gupta (DELIBERATE CONFLICT: Class 101 and 201 are both in Slot A1!)
MATCH (s:Student {reg_no: '21BCE1003'}), (cl:Class {class_id: '101'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1003'}), (cl:Class {class_id: '201'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1003'}), (cl:Class {class_id: '401'}) CREATE (s)-[:REGISTERED_IN]->(cl);

// Sneha Reddy
MATCH (s:Student {reg_no: '21BME2001'}), (cl:Class {class_id: '301'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BME2001'}), (cl:Class {class_id: '401'}) CREATE (s)-[:REGISTERED_IN]->(cl);

// Overbooking on Class 501 (AB1-201, Max Capacity 3, Enrolled 4)
MATCH (s:Student {reg_no: '21BCE1001'}), (cl:Class {class_id: '501'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1002'}), (cl:Class {class_id: '501'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1003'}), (cl:Class {class_id: '501'}) CREATE (s)-[:REGISTERED_IN]->(cl);
MATCH (s:Student {reg_no: '21BCE1005'}), (cl:Class {class_id: '501'}) CREATE (s)-[:REGISTERED_IN]->(cl);
