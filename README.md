# UniEnroll: FFCS Management Platform
> **Graph Database Architecture & Fully Flexible Credit System (FFCS) Platform**  
> Powered by **Neo4j**, **FastAPI**, **React 18**, **Tailwind CSS**, and **Cytoscape.js**.

---

## 🏛️ System Architecture Overview

UniEnroll is a full-stack academic registration engine designed around university **Fully Flexible Credit System (FFCS)** principles. The data model is powered by a high-performance **Neo4j Property Graph** that treats the `(:Class)` node as a centralized relational hub connecting students, faculty, venues, slots, and courses.

```
       (:Student)
           │
           │ [:REGISTERED_IN]
           ▼
        (:Class) ──[:FOR_COURSE]──► (:Course)
        /   │   \
       /    │    \
[:SCHEDULED_AT] [:HELD_IN] [:TAUGHT_BY]
     /      │       \
    ▼       ▼        ▼
 (:Slot) (:Venue) (:Faculty)
```

### Graph Schema & Node Specifications

| Node Label | Properties | Description |
| :--- | :--- | :--- |
| `(:Student)` | `reg_no`, `name`, `department`, `total_credits` | Enrolled undergraduate students |
| `(:Class)` | `class_id` | Central FFCS hub instance for a specific section |
| `(:Course)` | `course_code`, `title`, `credits`, `department` | Academic subjects with credit weight |
| `(:Slot)` | `slot_name`, `day`, `start_time`, `end_time` | Timetable time slots (e.g., A1, B1, C1, TA1) |
| `(:Venue)` | `building`, `room_no`, `capacity` | Physical classrooms (e.g., AB1-101, SMV-101) |
| `(:Faculty)` | `faculty_id`, `name`, `designation`, `department` | Professors instructing class sections |

### Graph Relationships

- `(:Student)-[:REGISTERED_IN]->(:Class)`
- `(:Class)-[:FOR_COURSE]->(:Course)`
- `(:Class)-[:SCHEDULED_AT]->(:Slot)`
- `(:Class)-[:HELD_IN]->(:Venue)`
- `(:Class)-[:TAUGHT_BY]->(:Faculty)`

---

## ⚡ Core Functional Modules

### 1. Interactive Student FFCS Registration & Timetable Matrix
- **Student Profile Switcher**: Switch between seeded VIT students (e.g., `21BCE1001` - Aarav Sharma, `21BCE1002` - Priya Patel, `21BCE1003` - Rohan Gupta, `21BME2001` - Sneha Reddy).
- **Weekly Slot-Based Timetable Grid**: Visual schedule matrix (Monday to Friday, Slots A1 to TD1) highlighting enrolled course code, room number, faculty, and credit badge.
- **Dynamic Credit Counter**: Live progress indicator against the standard FFCS credit cap (16 min – 27 max credits). Warns when cap is exceeded or minimum is unmet.
- **Interactive Cytoscape.js Topology Canvas**: Full interactive graph canvas mapping the student's sub-graph directly from Cypher:
  ```cypher
  MATCH p = (s:Student {reg_no: $reg_no})-[:REGISTERED_IN]->(cl:Class)-[:SCHEDULED_AT|HELD_IN|TAUGHT_BY|FOR_COURSE]->()
  RETURN p
  ```
  Supports zoom, fit, physics layouts (`cose`, `concentric`, `circle`), node inspection drawer, and toggling between individual student subgraphs and the global university network.

### 2. Course Discovery & Slot Exploration Engine
- **Slot Filtering**: Filter available courses by slot (e.g., find all courses running in slot `A1`, `B1`, etc.):
  ```cypher
  MATCH (s:Slot {slot_name: $slot_name})<-[:SCHEDULED_AT]-(cl:Class)-[:FOR_COURSE]->(c:Course)
  MATCH (cl)-[:TAUGHT_BY]->(f:Faculty)
  RETURN c.course_code AS Course_Code, c.title AS Course_Name, f.name AS Faculty, cl.class_id AS Class_ID
  ```
- **Real-Time Seat Availability**: Calculates available seats against room capacity (`v.capacity - count(students)`) with live capacity progress bars.
- **Pre-Registration Conflict Validation**: Running registration runs the conflict detection validator before inserting `:REGISTERED_IN`.

### 3. Smart Conflict & Clash Prevention Engine
- **Pre-Registration Validator**: Prevents registering into clashing slots:
  ```cypher
  MATCH (s:Student {reg_no: $reg_no})-[:REGISTERED_IN]->(cl1:Class)-[:SCHEDULED_AT]->(slot1:Slot)
  MATCH (target_cl:Class {class_id: $target_class_id})-[:SCHEDULED_AT]->(slot2:Slot)
  WHERE slot1.slot_name = slot2.slot_name
  RETURN slot1.slot_name AS Clashing_Slot, cl1.class_id AS Existing_Class
  ```
  If a clash exists, registration is blocked with a red conflict banner identifying the clashing slot and existing course.
- **Global Clash Audit Dashboard (Admin View)**:
  Audits the graph for concurrent registrations:
  ```cypher
  MATCH (s:Student)-[:REGISTERED_IN]->(cl1:Class)-[:SCHEDULED_AT]->(slot1:Slot),
        (s)-[:REGISTERED_IN]->(cl2:Class)-[:SCHEDULED_AT]->(slot2:Slot)
  WHERE cl1.class_id < cl2.class_id AND slot1.slot_name = slot2.slot_name
  RETURN s.name AS Student, s.reg_no AS Reg_No, cl1.class_id AS Class_1, cl2.class_id AS Class_2, slot1.slot_name AS Clashing_Slot
  ```
  Provides 1-click **Resolve Clash** buttons to drop either conflicting class immediately.
- **Pre-Registration Simulator**: Interactive test tool to preview conflict results for any student and any class before enrolling.

### 4. Classroom Capacity & Logistics Management
- **Overbooking Auditor**:
  ```cypher
  MATCH (v:Venue)<-[:HELD_IN]-(cl:Class)<-[:REGISTERED_IN]-(s:Student)
  WITH v, cl, count(s) AS Registered_Students
  RETURN v.building + '-' + v.room_no AS Venue, cl.class_id AS Class, v.capacity AS Max_Capacity, Registered_Students,
         (Registered_Students > v.capacity) AS Is_Overbooked
  ORDER BY Registered_Students DESC
  ```
  Flags classes where enrollment exceeds room capacity with an `Is_Overbooked` alert.
- **Empty Venue Finder (Smart Room Allocation)**:
  Filter by building (e.g. AB1, SMV, TT) and Slot to return all vacant rooms:
  ```cypher
  MATCH (v:Venue {building: $building})
  WHERE NOT EXISTS {
      MATCH (v)<-[:HELD_IN]-(cl:Class)-[:SCHEDULED_AT]->(s:Slot {slot_name: $slot_name})
  }
  RETURN v.room_no AS Room_No, v.capacity AS Capacity
  ```

### 5. Faculty Workload & Timetable View
- Dedicated schedule dashboard per professor:
  ```cypher
  MATCH (f:Faculty {name: $faculty_name})<-[:TAUGHT_BY]-(cl:Class)-[:SCHEDULED_AT]->(s:Slot),
        (cl)-[:HELD_IN]->(v:Venue),
        (cl)-[:FOR_COURSE]->(c:Course)
  RETURN f.name AS Faculty, c.course_code AS Course, cl.class_id AS Class, s.slot_name AS Slot, s.day AS Day, v.building + '-' + v.room_no AS Venue
  ```
  Displays weekly periods, total sections taught, and aggregate student headcounts.

### 6. Database & Seed Manager
- Live connection health indicator with node counts across all labels.
- In-app **Reset & Seed Demo Data** button with one-click restore.

---

## 🛠️ Tech Stack

- **Database**: Neo4j Graph Database 2026.09 (Bolt protocol)
- **Backend**: Python 3.14 + FastAPI + official `neo4j` Python driver + Uvicorn
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons
- **Graph Visualization**: Cytoscape.js (Force-directed `cose`, `concentric`, `circle`, `breadthfirst`)

---

## 🚀 Getting Started

### 1. Environment Configuration

The application reads database connection parameters from `.env` in the root directory:

```ini
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=vinee1871
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

### 2. Database Seeding

Run the automated Python seed script or use `seed.cypher`:

```bash
# Seed via Python script:
python3 seed.py

# Or inspect the raw Cypher file:
cat seed.cypher
```

**Seeded Test Cases Included:**
- `21BCE1001` (Aarav Sharma) - Clean 19 credits registration.
- `21BCE1002` (Priya Patel) - Registered across multiple courses.
- `21BCE1003` (Rohan Gupta) - **Deliberately seeded with a slot conflict in Slot A1** (enrolled in Class 101 and Class 201) to verify conflict detection.
- `Class 501` (Venue `AB1-201`, Capacity 3, Enrolled 4) - Deliberately seeded to test the **Overbooking Auditor**.

### 3. Running the Full-Stack Application

You can launch the complete application with a single command:

```bash
./run.sh
```

- **Web Application**: [http://localhost:8000](http://localhost:8000) (Serves the compiled React SPA + REST API)
- **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Vite Hot-Reload Server (Optional for frontend development)**:
  ```bash
  export PATH="$(pwd)/.toolchain/bin:$PATH"
  cd frontend
  npm run dev
  ```
  Accessible at [http://localhost:5173](http://localhost:5173)

---

## 📁 Repository Structure

```
UniEnroll_WebApp/
├── .env                          # Neo4j & Port configuration
├── run.sh                        # One-click startup runner
├── seed.py                       # Python CLI graph seed script
├── seed.cypher                   # Raw Cypher seed migration statements
├── requirements.txt              # Backend dependencies
├── backend/
│   ├── main.py                   # FastAPI application & SPA static server
│   ├── config.py                 # Configuration loader
│   ├── database.py               # Neo4j driver lifecycle & health checks
│   ├── services/
│   │   ├── student_service.py    # Student timetable, credits, registration
│   │   ├── course_service.py     # Slot exploration, course queries
│   │   ├── clash_service.py      # Pre-registration validator, global audit
│   │   ├── venue_service.py      # Overbooking auditor, vacant room finder
│   │   ├── faculty_service.py    # Faculty schedules and workload metrics
│   │   └── seed_service.py       # Graph schema constraints & VIT seed data
│   └── routers/
│       ├── students.py           # /api/students endpoints
│       ├── courses.py            # /api/courses endpoints
│       ├── clashes.py            # /api/clashes endpoints
│       ├── venues.py             # /api/venues endpoints
│       ├── faculty.py            # /api/faculty endpoints
│       ├── graph.py              # /api/graph (Cytoscape payload)
│       └── seed.py               # /api/seed management
└── frontend/
    ├── package.json              # React, Tailwind, Cytoscape dependencies
    ├── vite.config.ts            # Vite config with API proxy
    ├── tailwind.config.js        # Custom theme & colors
    ├── index.html                # App entry HTML
    └── src/
        ├── App.tsx               # Main application container & tab router
        ├── api.ts                # REST API client
        ├── types.ts              # TypeScript type definitions
        └── components/
            ├── Navbar.tsx        # Navigation, student switcher, DB status
            ├── StudentPortal/    # Timetable grid, CreditMeter, Cytoscape graph
            ├── CourseExplorer/   # Slot filters, seat availability, registration modal
            ├── ClashAudit/       # Global conflict table, pre-registration simulator
            ├── Logistics/        # Overbooking audit, empty room allocation
            ├── FacultyView/      # Professor teaching schedule & workload
            └── DatabaseManager/  # Graph statistics & Cypher reference
```

---

## 🛡️ License

MIT License - Developed for Academic FFCS Graph Architecture.
