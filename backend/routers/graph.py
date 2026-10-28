from fastapi import APIRouter, Depends, Query
from neo4j import Session
from typing import Optional
from ..database import get_db_session

router = APIRouter(prefix="/api/graph", tags=["Graph Visualizations"])

@router.get("/overview")
def get_graph_overview(
    limit: int = Query(100, description="Max elements to fetch"),
    session: Session = Depends(get_db_session)
):
    """
    Returns the complete university FFCS graph (Students, Classes, Courses, Slots, Venues, Faculty)
    formatted for Cytoscape.js.
    """
    query = """
    MATCH (cl:Class)
    OPTIONAL MATCH (s:Student)-[r_reg:REGISTERED_IN]->(cl)
    OPTIONAL MATCH (cl)-[r_course:FOR_COURSE]->(c:Course)
    OPTIONAL MATCH (cl)-[r_slot:SCHEDULED_AT]->(sl:Slot)
    OPTIONAL MATCH (cl)-[r_venue:HELD_IN]->(v:Venue)
    OPTIONAL MATCH (cl)-[r_faculty:TAUGHT_BY]->(f:Faculty)
    RETURN s, cl, c, sl, v, f
    LIMIT $limit
    """
    records = list(session.run(query, limit=limit))
    nodes_dict = {}
    edges_list = []

    for r in records:
        cl = r.get("cl")
        if cl:
            cid = cl["class_id"]
            class_id = f"class_{cid}"
            if class_id not in nodes_dict:
                nodes_dict[class_id] = {
                    "data": {
                        "id": class_id,
                        "label": f"Class {cid}",
                        "type": "Class",
                        "class_id": cid
                    }
                }

            s = r.get("s")
            if s:
                s_id = f"student_{s['reg_no']}"
                if s_id not in nodes_dict:
                    nodes_dict[s_id] = {
                        "data": {
                            "id": s_id,
                            "label": f"{s.get('name', 'Student')}\n({s['reg_no']})",
                            "type": "Student",
                            "reg_no": s["reg_no"],
                            "name": s.get("name")
                        }
                    }
                edges_list.append({
                    "data": {
                        "id": f"e_reg_{s['reg_no']}_{cid}",
                        "source": s_id,
                        "target": class_id,
                        "label": "REGISTERED_IN",
                        "type": "REGISTERED_IN"
                    }
                })

            c = r.get("c")
            if c:
                c_id = f"course_{c['course_code']}"
                if c_id not in nodes_dict:
                    nodes_dict[c_id] = {
                        "data": {
                            "id": c_id,
                            "label": f"{c['course_code']}\n{c.get('title', '')}",
                            "type": "Course",
                            "course_code": c["course_code"],
                            "credits": c.get("credits", 3)
                        }
                    }
                edges_list.append({
                    "data": {
                        "id": f"e_course_{cid}_{c['course_code']}",
                        "source": class_id,
                        "target": c_id,
                        "label": "FOR_COURSE",
                        "type": "FOR_COURSE"
                    }
                })

            sl = r.get("sl")
            if sl:
                sl_id = f"slot_{sl['slot_name']}"
                if sl_id not in nodes_dict:
                    nodes_dict[sl_id] = {
                        "data": {
                            "id": sl_id,
                            "label": f"Slot {sl['slot_name']}\n{sl.get('day', '')} {sl.get('start_time', '')}",
                            "type": "Slot",
                            "slot_name": sl["slot_name"]
                        }
                    }
                edges_list.append({
                    "data": {
                        "id": f"e_slot_{cid}_{sl['slot_name']}",
                        "source": class_id,
                        "target": sl_id,
                        "label": "SCHEDULED_AT",
                        "type": "SCHEDULED_AT"
                    }
                })

            v = r.get("v")
            if v:
                v_name = f"{v.get('building', 'BLD')}-{v.get('room_no', '000')}"
                v_id = f"venue_{v_name}"
                if v_id not in nodes_dict:
                    nodes_dict[v_id] = {
                        "data": {
                            "id": v_id,
                            "label": f"{v_name}\nCap: {v.get('capacity', 60)}",
                            "type": "Venue",
                            "venue_name": v_name
                        }
                    }
                edges_list.append({
                    "data": {
                        "id": f"e_venue_{cid}_{v_name}",
                        "source": class_id,
                        "target": v_id,
                        "label": "HELD_IN",
                        "type": "HELD_IN"
                    }
                })

            f = r.get("f")
            if f:
                f_name = f.get("name", "Faculty")
                f_id = f"faculty_{f.get('faculty_id', f.get('emp_id', f_name.replace(' ', '_')))}"
                if f_id not in nodes_dict:
                    nodes_dict[f_id] = {
                        "data": {
                            "id": f_id,
                            "label": f"{f_name}",
                            "type": "Faculty",
                            "faculty_name": f_name
                        }
                    }
                edges_list.append({
                    "data": {
                        "id": f"e_fac_{cid}_{f_id}",
                        "source": class_id,
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
