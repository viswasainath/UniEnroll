from neo4j import Session
from typing import List, Dict, Any, Optional
from ..config import MAX_CREDIT_CAP, MIN_CREDIT_CAP

class StudentService:
    @staticmethod
    def get_all_students(session: Session) -> List[Dict[str, Any]]:
        query = """
        MATCH (s:Student)
        OPTIONAL MATCH (s)-[:REGISTERED_IN]->(cl:Class)-[:FOR_COURSE]->(c:Course)
        RETURN s.reg_no AS reg_no, 
               s.name AS name,
               coalesce(s.department, s.program, 'CSE') AS department,
               coalesce(sum(c.credits), 0) AS total_credits,
               count(cl) AS registered_class_count
        ORDER BY s.reg_no ASC
        """
        result = session.run(query)
        students = []
        for record in result:
            students.append({
                "reg_no": record["reg_no"],
                "name": record["name"],
                "department": record["department"],
                "total_credits": record["total_credits"],
                "registered_class_count": record["registered_class_count"],
                "is_over_cap": record["total_credits"] > MAX_CREDIT_CAP,
                "is_under_min": record["total_credits"] < MIN_CREDIT_CAP
            })
        return students

    @staticmethod
    def get_student_profile(session: Session, reg_no: str) -> Optional[Dict[str, Any]]:
        query = """
        MATCH (s:Student {reg_no: $reg_no})
        OPTIONAL MATCH (s)-[:REGISTERED_IN]->(cl:Class)-[:FOR_COURSE]->(c:Course)
        RETURN s.reg_no AS reg_no,
               s.name AS name,
               coalesce(s.department, s.program, 'CSE') AS department,
               coalesce(sum(c.credits), 0) AS total_credits,
               count(cl) AS registered_class_count
        """
        record = session.run(query, reg_no=reg_no).single()
        if not record or not record["reg_no"]:
            return None
        return {
            "reg_no": record["reg_no"],
            "name": record["name"],
            "department": record["department"],
            "total_credits": record["total_credits"],
            "registered_class_count": record["registered_class_count"],
            "max_credit_cap": MAX_CREDIT_CAP,
            "min_credit_cap": MIN_CREDIT_CAP,
            "credits_remaining": max(0, MAX_CREDIT_CAP - record["total_credits"]),
            "is_over_cap": record["total_credits"] > MAX_CREDIT_CAP,
            "is_under_min": record["total_credits"] < MIN_CREDIT_CAP
        }

    @staticmethod
    def get_student_timetable(session: Session, reg_no: str) -> Dict[str, Any]:
        query = """
        MATCH (s:Student {reg_no: $reg_no})-[:REGISTERED_IN]->(cl:Class)
        OPTIONAL MATCH (cl)-[:FOR_COURSE]->(c:Course)
        OPTIONAL MATCH (cl)-[:SCHEDULED_AT]->(sl:Slot)
        OPTIONAL MATCH (cl)-[:HELD_IN]->(v:Venue)
        OPTIONAL MATCH (cl)-[:TAUGHT_BY]->(f:Faculty)
        RETURN cl.class_id AS class_id,
               c.course_code AS course_code,
               c.title AS course_title,
               coalesce(c.credits, 3) AS credits,
               coalesce(c.department, 'CSE') AS course_dept,
               sl.slot_name AS slot_name,
               sl.day AS day,
               sl.start_time AS start_time,
               sl.end_time AS end_time,
               coalesce(v.building + '-' + v.room_no, 'TBA') AS venue,
               coalesce(v.capacity, 60) AS venue_capacity,
               coalesce(f.name, 'TBA') AS faculty_name,
               coalesce(f.department, f.school, 'Faculty') AS faculty_dept
        ORDER BY sl.day, sl.start_time
        """
        records = list(session.run(query, reg_no=reg_no))
        classes = []
        slot_map = {}
        slot_counts = {}
        total_credits = 0

        for r in records:
            c_info = {
                "class_id": r["class_id"],
                "course_code": r["course_code"],
                "course_title": r["course_title"],
                "credits": r["credits"],
                "course_dept": r["course_dept"],
                "slot_name": r["slot_name"],
                "day": r["day"],
                "start_time": r["start_time"],
                "end_time": r["end_time"],
                "venue": r["venue"],
                "venue_capacity": r["venue_capacity"],
                "faculty_name": r["faculty_name"],
                "faculty_dept": r["faculty_dept"],
                "has_clash": False
            }
            classes.append(c_info)
            slot_name = r["slot_name"]
            slot_counts[slot_name] = slot_counts.get(slot_name, 0) + 1
            if slot_name:
                if slot_name not in slot_map:
                    slot_map[slot_name] = []
                slot_map[slot_name].append(c_info)
            total_credits += (r["credits"] or 0)

        # Mark clashes if more than 1 class in the same slot
        clashing_slots = [s for s, count in slot_counts.items() if count > 1]
        for c in classes:
            if c["slot_name"] in clashing_slots:
                c["has_clash"] = True

        return {
            "reg_no": reg_no,
            "classes": classes,
            "slot_map": slot_map,
            "total_credits": total_credits,
            "clashing_slots": clashing_slots,
            "has_clashes": len(clashing_slots) > 0,
            "is_over_cap": total_credits > MAX_CREDIT_CAP,
            "max_credit_cap": MAX_CREDIT_CAP,
            "min_credit_cap": MIN_CREDIT_CAP
        }

    @staticmethod
    def get_student_graph_data(session: Session, reg_no: str) -> Dict[str, Any]:
        """
        Executes:
        MATCH p = (s:Student {reg_no: $reg_no})-[:REGISTERED_IN]->(cl:Class)-[:SCHEDULED_AT|HELD_IN|TAUGHT_BY|FOR_COURSE]->()
        RETURN p
        And formats for Cytoscape.js
        """
        query = """
        MATCH (s:Student {reg_no: $reg_no})
        OPTIONAL MATCH (s)-[r_reg:REGISTERED_IN]->(cl:Class)
        OPTIONAL MATCH (cl)-[r_course:FOR_COURSE]->(c:Course)
        OPTIONAL MATCH (cl)-[r_slot:SCHEDULED_AT]->(sl:Slot)
        OPTIONAL MATCH (cl)-[r_venue:HELD_IN]->(v:Venue)
        OPTIONAL MATCH (cl)-[r_faculty:TAUGHT_BY]->(f:Faculty)
        RETURN s, cl, c, sl, v, f
        """
        result = session.run(query, reg_no=reg_no)
        nodes_dict = {}
        edges_list = []

        for record in result:
            s = record.get("s")
            if s and s["reg_no"] not in nodes_dict:
                nodes_dict[s["reg_no"]] = {
                    "data": {
                        "id": f"student_{s['reg_no']}",
                        "label": f"{s.get('name', 'Student')}\n({s['reg_no']})",
                        "type": "Student",
                        "reg_no": s["reg_no"],
                        "name": s.get("name"),
                        "department": s.get("department", s.get("program", "CSE"))
                    }
                }

            cl = record.get("cl")
            if cl:
                cid = cl["class_id"]
                class_node_id = f"class_{cid}"
                if class_node_id not in nodes_dict:
                    nodes_dict[class_node_id] = {
                        "data": {
                            "id": class_node_id,
                            "label": f"Class {cid}",
                            "type": "Class",
                            "class_id": cid
                        }
                    }
                # Edge Student -> Class
                edges_list.append({
                    "data": {
                        "id": f"reg_{s['reg_no']}_{cid}",
                        "source": f"student_{s['reg_no']}",
                        "target": class_node_id,
                        "label": "REGISTERED_IN",
                        "type": "REGISTERED_IN"
                    }
                })

                c = record.get("c")
                if c:
                    c_id = f"course_{c['course_code']}"
                    if c_id not in nodes_dict:
                        nodes_dict[c_id] = {
                            "data": {
                                "id": c_id,
                                "label": f"{c['course_code']}\n{c.get('title', '')} ({c.get('credits', 3)} Cr)",
                                "type": "Course",
                                "course_code": c["course_code"],
                                "title": c.get("title"),
                                "credits": c.get("credits", 3)
                            }
                        }
                    edges_list.append({
                        "data": {
                            "id": f"for_{cid}_{c['course_code']}",
                            "source": class_node_id,
                            "target": c_id,
                            "label": "FOR_COURSE",
                            "type": "FOR_COURSE"
                        }
                    })

                sl = record.get("sl")
                if sl:
                    slot_id = f"slot_{sl['slot_name']}"
                    if slot_id not in nodes_dict:
                        nodes_dict[slot_id] = {
                            "data": {
                                "id": slot_id,
                                "label": f"Slot {sl['slot_name']}\n{sl.get('day', '')} {sl.get('start_time', '')}-{sl.get('end_time', '')}",
                                "type": "Slot",
                                "slot_name": sl["slot_name"],
                                "day": sl.get("day"),
                                "start_time": sl.get("start_time"),
                                "end_time": sl.get("end_time")
                            }
                        }
                    edges_list.append({
                        "data": {
                            "id": f"sched_{cid}_{sl['slot_name']}",
                            "source": class_node_id,
                            "target": slot_id,
                            "label": "SCHEDULED_AT",
                            "type": "SCHEDULED_AT"
                        }
                    })

                v = record.get("v")
                if v:
                    v_name = f"{v.get('building', 'BLD')}-{v.get('room_no', '000')}"
                    v_id = f"venue_{v_name}"
                    if v_id not in nodes_dict:
                        nodes_dict[v_id] = {
                            "data": {
                                "id": v_id,
                                "label": f"Room {v_name}\nCap: {v.get('capacity', 60)}",
                                "type": "Venue",
                                "venue_name": v_name,
                                "building": v.get("building"),
                                "room_no": v.get("room_no"),
                                "capacity": v.get("capacity", 60)
                            }
                        }
                    edges_list.append({
                        "data": {
                            "id": f"held_{cid}_{v_name}",
                            "source": class_node_id,
                            "target": v_id,
                            "label": "HELD_IN",
                            "type": "HELD_IN"
                        }
                    })

                f = record.get("f")
                if f:
                    f_name = f.get("name", "Faculty")
                    f_id = f"faculty_{f.get('emp_id', f.get('faculty_id', f_name.replace(' ', '_')))}"
                    if f_id not in nodes_dict:
                        nodes_dict[f_id] = {
                            "data": {
                                "id": f_id,
                                "label": f"{f_name}\n{f.get('school', f.get('department', 'Faculty'))}",
                                "type": "Faculty",
                                "faculty_name": f_name,
                                "department": f.get("school", f.get("department", "Faculty"))
                            }
                        }
                    edges_list.append({
                        "data": {
                            "id": f"taught_{cid}_{f_id}",
                            "source": class_node_id,
                            "target": f_id,
                            "label": "TAUGHT_BY",
                            "type": "TAUGHT_BY"
                        }
                    })

        # Deduplicate edges
        seen_edges = set()
        deduped_edges = []
        for e in edges_list:
            edge_key = (e["data"]["source"], e["data"]["target"], e["data"]["label"])
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                deduped_edges.append(e)

        return {
            "elements": {
                "nodes": list(nodes_dict.values()),
                "edges": deduped_edges
            }
        }

    @staticmethod
    def register_class(session: Session, reg_no: str, target_class_id: str) -> Dict[str, Any]:
        """
        Validates:
        1. Class exists
        2. Student exists
        3. Already registered?
        4. Slot Clash Check
        5. Credit Cap Check
        6. Venue Capacity Check
        Registers if all validations pass.
        """
        # Check student
        student_check = session.run("MATCH (s:Student {reg_no: $reg_no}) RETURN s", reg_no=reg_no).single()
        if not student_check:
            return {"success": False, "error_type": "STUDENT_NOT_FOUND", "message": f"Student with reg_no '{reg_no}' not found."}

        # Check target class
        target_class = session.run("""
            MATCH (cl:Class {class_id: $target_class_id})
            OPTIONAL MATCH (cl)-[:FOR_COURSE]->(c:Course)
            OPTIONAL MATCH (cl)-[:SCHEDULED_AT]->(sl:Slot)
            OPTIONAL MATCH (cl)-[:HELD_IN]->(v:Venue)
            RETURN cl.class_id AS class_id, c.course_code AS course_code, c.title AS course_title,
                   coalesce(c.credits, 3) AS credits, sl.slot_name AS slot_name, v.capacity AS capacity,
                   v.building + '-' + v.room_no AS venue_name
        """, target_class_id=target_class_id).single()

        if not target_class:
            return {"success": False, "error_type": "CLASS_NOT_FOUND", "message": f"Class '{target_class_id}' does not exist."}

        # Check if already registered
        already_reg = session.run("""
            MATCH (s:Student {reg_no: $reg_no})-[:REGISTERED_IN]->(cl:Class {class_id: $target_class_id})
            RETURN count(cl) AS cnt
        """, reg_no=reg_no, target_class_id=target_class_id).single()["cnt"] > 0

        if already_reg:
            return {"success": False, "error_type": "ALREADY_REGISTERED", "message": "You are already registered in this class."}

        # Check if student is already registered for this COURSE in another class section
        course_already_taken = session.run("""
            MATCH (s:Student {reg_no: $reg_no})-[:REGISTERED_IN]->(cl:Class)-[:FOR_COURSE]->(c:Course {course_code: $course_code})
            RETURN cl.class_id AS existing_class_id
        """, reg_no=reg_no, course_code=target_class["course_code"]).single()

        if course_already_taken:
            return {
                "success": False,
                "error_type": "DUPLICATE_COURSE",
                "message": f"You are already registered for course {target_class['course_code']} in Class {course_already_taken['existing_class_id']}."
            }

        # Slot Clash Check
        clash_check = session.run("""
            MATCH (s:Student {reg_no: $reg_no})-[:REGISTERED_IN]->(cl1:Class)-[:SCHEDULED_AT]->(slot1:Slot)
            MATCH (target_cl:Class {class_id: $target_class_id})-[:SCHEDULED_AT]->(slot2:Slot)
            MATCH (cl1)-[:FOR_COURSE]->(existing_c:Course)
            WHERE slot1.slot_name = slot2.slot_name
            RETURN slot1.slot_name AS Clashing_Slot, 
                   cl1.class_id AS Existing_Class,
                   existing_c.course_code AS Existing_Course,
                   existing_c.title AS Existing_Title
        """, reg_no=reg_no, target_class_id=target_class_id).data()

        if clash_check:
            clash = clash_check[0]
            return {
                "success": False,
                "error_type": "SLOT_CLASH",
                "clashing_slot": clash["Clashing_Slot"],
                "existing_class": clash["Existing_Class"],
                "existing_course": clash["Existing_Course"],
                "existing_title": clash["Existing_Title"],
                "target_class": target_class_id,
                "target_course": target_class["course_code"],
                "message": f"Slot Clash Detected! Target class occupies slot '{clash['Clashing_Slot']}', which conflicts with your existing registration in Class {clash['Existing_Class']} ({clash['Existing_Course']} - {clash['Existing_Title']})."
            }

        # Credit Cap Check
        current_credits_res = session.run("""
            MATCH (s:Student {reg_no: $reg_no})-[:REGISTERED_IN]->(cl:Class)-[:FOR_COURSE]->(c:Course)
            RETURN coalesce(sum(c.credits), 0) AS total
        """, reg_no=reg_no).single()["total"]

        projected = current_credits_res + target_class["credits"]
        if projected > MAX_CREDIT_CAP:
            return {
                "success": False,
                "error_type": "CREDIT_LIMIT_EXCEEDED",
                "current_credits": current_credits_res,
                "target_credits": target_class["credits"],
                "projected_credits": projected,
                "max_limit": MAX_CREDIT_CAP,
                "message": f"Credit cap exceeded! Registering adds {target_class['credits']} credits, totaling {projected} credits (maximum allowed is {MAX_CREDIT_CAP})."
            }

        # Venue Capacity Check
        capacity_res = session.run("""
            MATCH (cl:Class {class_id: $target_class_id})-[:HELD_IN]->(v:Venue)
            OPTIONAL MATCH (s:Student)-[:REGISTERED_IN]->(cl)
            RETURN v.capacity AS capacity, count(s) AS registered_count
        """, target_class_id=target_class_id).single()

        if capacity_res and capacity_res["capacity"] is not None:
            if capacity_res["registered_count"] >= capacity_res["capacity"]:
                return {
                    "success": False,
                    "error_type": "VENUE_FULL",
                    "capacity": capacity_res["capacity"],
                    "enrolled": capacity_res["registered_count"],
                    "message": f"Class capacity full! Venue has {capacity_res['capacity']} seats, all currently filled."
                }

        # If all checks pass, register the student
        session.run("""
            MATCH (s:Student {reg_no: $reg_no}), (cl:Class {class_id: $target_class_id})
            MERGE (s)-[:REGISTERED_IN]->(cl)
        """, reg_no=reg_no, target_class_id=target_class_id)

        return {
            "success": True,
            "message": f"Successfully registered into Class {target_class_id} ({target_class['course_code']} - {target_class['course_title']}) in Slot {target_class['slot_name']}!",
            "class_id": target_class_id,
            "course_code": target_class["course_code"],
            "credits": target_class["credits"],
            "slot": target_class["slot_name"]
        }

    @staticmethod
    def drop_class(session: Session, reg_no: str, class_id: str) -> Dict[str, Any]:
        result = session.run("""
            MATCH (s:Student {reg_no: $reg_no})-[r:REGISTERED_IN]->(cl:Class {class_id: $class_id})
            DELETE r
            RETURN count(r) AS deleted
        """, reg_no=reg_no, class_id=class_id).single()

        deleted = result["deleted"] if result else 0
        if deleted > 0:
            return {"success": True, "message": f"Successfully dropped Class {class_id}."}
        else:
            return {"success": False, "message": f"Registration for Class {class_id} not found."}
