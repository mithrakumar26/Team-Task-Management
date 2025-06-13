import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go

API_BASE_URL = "http://localhost:8000"

if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'selected_task_id' not in st.session_state:
    st.session_state.selected_task_id = None
if 'show_task_details' not in st.session_state:
    st.session_state.show_task_details = {}

def make_request(method, endpoint, data=None, params=None):
    """Make API request with authentication"""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 401:
            st.session_state.token = None
            st.session_state.user_info = None
            st.error("⚠️ Session expired. Please login again.")
            st.rerun()
        
        return response
    except requests.exceptions.ConnectionError:
        st.error("🚫 Cannot connect to API. Make sure the backend server is running.")
        return None

def show_task_analytics():
    st.subheader("📊 Task Analytics")
    
    response = make_request("GET", "/tasks")
    if response and response.status_code == 200:
        tasks = response.json()
        if tasks:
            df = pd.DataFrame(tasks)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tasks", len(tasks))
            with col2:
                completed = len(df[df['status'] == 'completed'])
                st.metric("Completed", completed)
            with col3:
                in_progress = len(df[df['status'] == 'in_progress'])
                st.metric("In Progress", in_progress)
            with col4:
                pending = len(df[df['status'] == 'pending'])
                st.metric("Pending", pending)
            
            col1, col2 = st.columns(2)
            with col1:
                status_counts = df['status'].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, 
                           title="Task Status Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                priority_counts = df['priority'].value_counts()
                fig = px.bar(x=priority_counts.index, y=priority_counts.values,
                           title="Task Priority Distribution")
                st.plotly_chart(fig, use_container_width=True)

def login_page():
    st.title("🔐 Team Task Management System")
    st.markdown("### Welcome! Please login to continue")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("login_form", clear_on_submit=True):
                    st.markdown("#### Login to your account")
                    username = st.text_input("👤 Username", placeholder="Enter your username")
                    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                    
                    col_login, col_clear = st.columns(2)
                    with col_login:
                        submit = st.form_submit_button("🚀 Login", use_container_width=True)
                    
                    if submit:
                        if username and password:
                            with st.spinner("Authenticating..."):
                                response = make_request("POST", "/auth/login", {
                                    "username": username,
                                    "password": password
                                })
                                
                                if response and response.status_code == 200:
                                    token_data = response.json()
                                    st.session_state.token = token_data["access_token"]
                                    
                                    user_response = make_request("GET", "/auth/me")
                                    if user_response and user_response.status_code == 200:
                                        st.session_state.user_info = user_response.json()
                                        st.success("✅ Login successful!")
                                        st.balloons()
                                        st.rerun()
                                else:
                                    st.error("❌ Invalid credentials. Please try again.")
                        else:
                            st.warning("⚠️ Please fill in all fields")
    
    with tab2:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("register_form", clear_on_submit=True):
                    st.markdown("#### Create new account")
                    reg_username = st.text_input("👤 Username", key="reg_username", placeholder="Choose a username")
                    reg_email = st.text_input("📧 Email", key="reg_email", placeholder="Enter your email")
                    reg_password = st.text_input("🔒 Password", type="password", key="reg_password", placeholder="Create a password")
                    reg_role = st.selectbox("👥 Role", ["user", "admin"], key="reg_role")
                    
                    submit_reg = st.form_submit_button("📝 Register", use_container_width=True)
                    
                    if submit_reg:
                        if reg_username and reg_email and reg_password:
                            with st.spinner("Creating account..."):
                                response = make_request("POST", "/auth/register", {
                                    "username": reg_username,
                                    "email": reg_email,
                                    "password": reg_password,
                                    "role": reg_role
                                })
                                
                                if response and response.status_code == 200:
                                    st.success("✅ Registration successful! Please login with your credentials.")
                                else:
                                    st.error("❌ Registration failed. Username or email may already exist.")
                        else:
                            st.warning("⚠️ Please fill in all fields")

def create_project_form():
    with st.expander("➕ Create New Project", expanded=False):
        with st.form("create_project", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("📋 Project Title", placeholder="Enter project title")
            with col2:
                status = st.selectbox("📊 Status", ["active", "completed", "on_hold"])
            
            description = st.text_area("📝 Description", placeholder="Enter project description", height=100)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                submit = st.form_submit_button("🚀 Create Project", use_container_width=True)
            
            if submit and title:
                with st.spinner("Creating project..."):
                    response = make_request("POST", "/projects", {
                        "title": title,
                        "description": description,
                        "status": status
                    })
                    
                    if response and response.status_code == 200:
                        st.success("✅ Project created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create project")
            elif submit:
                st.warning("⚠️ Project title is required")

def display_projects():
    response = make_request("GET", "/projects")
    if response and response.status_code == 200:
        projects = response.json()
        if projects:
            for i, project in enumerate(projects):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.markdown(f"### 📋 {project['title']}")
                    with col2:
                        status_color = {"active": "🟢", "completed": "✅", "on_hold": "🟡"}
                        st.write(f"{status_color.get(project.get('status', 'active'), '🔵')} {project.get('status', 'active').title()}")
                    with col3:
                        if st.button("✏️ Edit", key=f"edit_proj_{project['id']}", use_container_width=True):
                            st.session_state[f"edit_project_{project['id']}"] = True
                    with col4:
                        if st.button("🗑️ Delete", key=f"del_proj_{project['id']}", use_container_width=True):
                            st.session_state[f"confirm_delete_project_{project['id']}"] = True
                    
                    if project.get('description'):
                        st.markdown(f"*{project['description']}*")

                    if st.session_state.get(f"confirm_delete_project_{project['id']}", False):
                        st.warning("⚠️ Are you sure you want to delete this project?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Yes, Delete", key=f"confirm_yes_{project['id']}"):
                                response = make_request("DELETE", f"/projects/{project['id']}")
                                if response and response.status_code == 200:
                                    st.success("✅ Project deleted!")
                                    st.rerun()
                        with col2:
                            if st.button("❌ Cancel", key=f"confirm_no_{project['id']}"):
                                st.session_state[f"confirm_delete_project_{project['id']}"] = False
                                st.rerun()
                    
                    if st.session_state.get(f"edit_project_{project['id']}", False):
                        with st.form(f"edit_project_{project['id']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                new_title = st.text_input("Title", value=project['title'])
                            with col2:
                                new_status = st.selectbox("Status", ["active", "completed", "on_hold"], 
                                                        index=["active", "completed", "on_hold"].index(project.get('status', 'active')))
                            new_description = st.text_area("Description", value=project.get('description', ''))
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                save = st.form_submit_button("💾 Save Changes")
                            with col_cancel:
                                cancel = st.form_submit_button("❌ Cancel")
                            
                            if save:
                                response = make_request("PUT", f"/projects/{project['id']}", {
                                    "title": new_title,
                                    "description": new_description,
                                    "status": new_status
                                })
                                if response and response.status_code == 200:
                                    st.success("✅ Project updated!")
                                    st.session_state[f"edit_project_{project['id']}"] = False
                                    st.rerun()
                            
                            if cancel:
                                st.session_state[f"edit_project_{project['id']}"] = False
                                st.rerun()
                    
                    st.divider()
        else:
            st.info("📝 No projects found. Create your first project above!")

def create_task_form():
    with st.expander("➕ Create New Task", expanded=False):
        projects_response = make_request("GET", "/projects")
        users_response = make_request("GET", "/users")
        
        if projects_response and users_response:
            projects = projects_response.json()
            users = users_response.json()
            
            with st.form("create_task", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("📋 Task Title", placeholder="Enter task title")
                    
                    if projects:
                        project_options = {p['title']: p['id'] for p in projects}
                        selected_project = st.selectbox("🏗️ Project", list(project_options.keys()))
                        project_id = project_options.get(selected_project)
                    else:
                        st.error("❌ No projects available. Create a project first.")
                        project_id = None
                
                with col2:
                    priority = st.selectbox("⚡ Priority", ["low", "medium", "high"], index=1)
                    
                    if users:
                        user_options = {u['username']: u['id'] for u in users if u['role'] == 'user'}
                        if user_options:
                            selected_user = st.selectbox("👤 Assign to", list(user_options.keys()))
                            assignee_id = user_options.get(selected_user)
                        else:
                            st.error("❌ No users available.")
                            assignee_id = None
                    else:
                        assignee_id = None
                
                description = st.text_area("📝 Description", placeholder="Enter task description", height=100)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    deadline = st.date_input("📅 Deadline", min_value=date.today())
                with col2:
                    estimated_hours = st.number_input("⏱️ Estimated Hours", min_value=0.5, max_value=100.0, value=1.0, step=0.5)
                with col3:
                    status = st.selectbox("📊 Status", ["pending", "in_progress", "completed"])
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    submit = st.form_submit_button("🚀 Create Task", use_container_width=True)
                
                if submit and title and project_id and assignee_id:
                    with st.spinner("Creating task..."):
                        task_data = {
                            "title": title,
                            "description": description,
                            "project_id": project_id,
                            "assignee_id": assignee_id,
                            "deadline": deadline.isoformat() + "T00:00:00",
                            "priority": priority,
                            "status": status,
                            "estimated_hours": estimated_hours
                        }
                        
                        response = make_request("POST", "/tasks", task_data)
                        if response and response.status_code == 200:
                            st.success("✅ Task created successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to create task")
                elif submit:
                    st.warning("⚠️ Please fill in all required fields")

def display_tasks_interactive():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_filter = st.selectbox("📊 Status", ["All", "pending", "in_progress", "completed"])
    with col2:
        priority_filter = st.selectbox("⚡ Priority", ["All", "low", "medium", "high"])
    with col3:
        sort_by = st.selectbox("📋 Sort by", ["deadline", "priority", "created_at", "title"])
    with col4:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    params = {}
    if status_filter != "All":
        params["status"] = status_filter
    if priority_filter != "All":
        params["priority"] = priority_filter
    
    response = make_request("GET", "/tasks", params=params)
    if response and response.status_code == 200:
        tasks = response.json()
        if tasks:
            if sort_by == "priority":
                priority_order = {"high": 3, "medium": 2, "low": 1}
                tasks.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
            elif sort_by == "deadline" and any(t.get('deadline') for t in tasks):
                tasks.sort(key=lambda x: x.get('deadline', '9999-12-31'))
            
            for task in tasks:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    
                    with col1:
                        priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                        status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
                        st.markdown(f"### {priority_emoji.get(task['priority'], '🔵')} {task['title']}")
                        st.markdown(f"{status_emoji.get(task['status'], '📋')} {task['status'].replace('_', ' ').title()}")
                    
                    with col2:
                        if task.get('deadline'):
                            deadline = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
                            days_left = (deadline.date() - date.today()).days
                            if days_left < 0:
                                st.markdown(f"⚠️ **Overdue by {abs(days_left)} days**")
                            elif days_left == 0:
                                st.markdown("🚨 **Due Today**")
                            else:
                                st.markdown(f"📅 Due in {days_left} days")
                    
                    with col3:
                        if st.button("👁️ View", key=f"view_task_{task['id']}", use_container_width=True):
                            st.session_state.show_task_details[task['id']] = not st.session_state.show_task_details.get(task['id'], False)
                    
                    with col4:
                        if st.button("✏️ Edit", key=f"edit_task_{task['id']}", use_container_width=True):
                            st.session_state[f"edit_task_{task['id']}"] = True
                    
                    with col5:
                        if st.button("🗑️ Delete", key=f"del_task_{task['id']}", use_container_width=True):
                            st.session_state[f"confirm_delete_task_{task['id']}"] = True

                    if st.session_state.show_task_details.get(task['id'], False):
                        with st.expander("📋 Task Details", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**📝 Description:** {task.get('description', 'No description')}")
                                st.write(f"**👤 Assignee ID:** {task.get('assignee_id', 'Unassigned')}")
                            with col2:
                                st.write(f"**🏗️ Project ID:** {task.get('project_id', 'No project')}")
                                st.write(f"**⏱️ Estimated Hours:** {task.get('estimated_hours', 'Not specified')}")
                    
                    if st.session_state.get(f"confirm_delete_task_{task['id']}", False):
                        st.warning("⚠️ Are you sure you want to delete this task?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Yes, Delete", key=f"confirm_yes_task_{task['id']}"):
                                response = make_request("DELETE", f"/tasks/{task['id']}")
                                if response and response.status_code == 200:
                                    st.success("✅ Task deleted!")
                                    st.rerun()
                        with col2:
                            if st.button("❌ Cancel", key=f"confirm_no_task_{task['id']}"):
                                st.session_state[f"confirm_delete_task_{task['id']}"] = False
                                st.rerun()
                    
                    if st.session_state.get(f"edit_task_{task['id']}", False):
                        with st.form(f"edit_task_{task['id']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                new_title = st.text_input("Title", value=task['title'])
                                new_status = st.selectbox("Status", ["pending", "in_progress", "completed"], 
                                                        index=["pending", "in_progress", "completed"].index(task['status']))
                            with col2:
                                new_priority = st.selectbox("Priority", ["low", "medium", "high"],
                                                          index=["low", "medium", "high"].index(task['priority']))
                                new_estimated_hours = st.number_input("Estimated Hours", value=float(task.get('estimated_hours', 1.0)))
                            
                            new_description = st.text_area("Description", value=task.get('description', ''))
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                save = st.form_submit_button("💾 Save Changes")
                            with col_cancel:
                                cancel = st.form_submit_button("❌ Cancel")
                            
                            if save:
                                update_data = {
                                    "title": new_title,
                                    "description": new_description,
                                    "status": new_status,
                                    "priority": new_priority,
                                    "estimated_hours": new_estimated_hours
                                }
                                response = make_request("PUT", f"/tasks/{task['id']}", update_data)
                                if response and response.status_code == 200:
                                    st.success("✅ Task updated!")
                                    st.session_state[f"edit_task_{task['id']}"] = False
                                    st.rerun()
                            
                            if cancel:
                                st.session_state[f"edit_task_{task['id']}"] = False
                                st.rerun()
                    
                    st.divider()
        else:
            st.info("📝 No tasks found matching your filters. Create a new task above!")

def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    
    show_task_analytics()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏗️ Projects", "📋 Tasks", "👥 Users", "💬 Comments", "📊 Reports"])
    
    with tab1:
        st.subheader("🏗️ Project Management")
        create_project_form()
        st.subheader("📋 Existing Projects")
        display_projects()
    
    with tab2:
        st.subheader("📋 Task Management")
        create_task_form()
        st.subheader("📝 All Tasks")
        display_tasks_interactive()
    
    with tab3:
        st.subheader("👥 User Management")
        response = make_request("GET", "/users")
        if response and response.status_code == 200:
            users = response.json()
            if users:
                for user in users:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        with col1:
                            role_emoji = {"admin": "👨‍💼", "user": "👤"}
                            st.write(f"{role_emoji.get(user['role'], '👤')} **{user['username']}**")
                            st.write(f"📧 {user['email']}")
                        with col2:
                            status_emoji = "✅" if user['is_active'] else "❌"
                            st.write(f"{status_emoji} {'Active' if user['is_active'] else 'Inactive'}")
                        with col3:
                            st.write(f"**Role:** {user['role'].title()}")
                        with col4:
                            created = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
                            st.write(f"**Joined:** {created.strftime('%Y-%m-%d')}")
                        st.divider()
            else:
                st.info("👥 No users found")
    
    with tab4:
        st.subheader("💬 Task Comments Management")
        
        response = make_request("GET", "/tasks")
        if response and response.status_code == 200:
            tasks = response.json()
            if tasks:
                task_options = {f"{t['title']} (ID: {t['id']})": t['id'] for t in tasks}
                selected_task = st.selectbox("📋 Select Task to View Comments", list(task_options.keys()))
                task_id = task_options.get(selected_task)
                
                if task_id:
                    comments_response = make_request("GET", f"/tasks/{task_id}/comments")
                    if comments_response and comments_response.status_code == 200:
                        comments = comments_response.json()
                        if comments:
                            st.subheader("💬 Comments")
                            for comment in comments:
                                with st.container():
                                    st.markdown(f"**👤 User ID {comment['author_id']}** - 📅 {comment['created_at']}")
                                    st.markdown(f"💬 {comment['content']}")
                                    st.divider()
                        else:
                            st.info("💬 No comments for this task")
    
    with tab5:
        st.subheader("📊 Reports & Analytics")
        
        response = make_request("GET", "/tasks")
        if response and response.status_code == 200:
            tasks = response.json()
            if tasks:
                df = pd.DataFrame(tasks)

                if 'created_at' in df.columns:
                    df['created_date'] = pd.to_datetime(df['created_at']).dt.date
                    daily_tasks = df.groupby(['created_date', 'status']).size().unstack(fill_value=0)
                    
                    if not daily_tasks.empty:
                        fig = px.area(daily_tasks, title="Task Creation Over Time by Status")
                        st.plotly_chart(fig, use_container_width=True)

                if len(df) > 0:
                    priority_status = pd.crosstab(df['priority'], df['status'])
                    fig = px.imshow(priority_status, title="Priority vs Status Heatmap", 
                                  labels=dict(x="Status", y="Priority", color="Count"))
                    st.plotly_chart(fig, use_container_width=True)

def user_dashboard():
    st.title("👤 User Dashboard")

    response = make_request("GET", "/tasks")
    if response and response.status_code == 200:
        tasks = response.json()
        user_tasks = [t for t in tasks if t.get('assignee_id') == st.session_state.user_info.get('id')]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 My Tasks", len(user_tasks))
        with col2:
            completed = len([t for t in user_tasks if t['status'] == 'completed'])
            st.metric("✅ Completed", completed)
        with col3:
            in_progress = len([t for t in user_tasks if t['status'] == 'in_progress'])
            st.metric("🔄 In Progress", in_progress)
        with col4:
            pending = len([t for t in user_tasks if t['status'] == 'pending'])
            st.metric("⏳ Pending", pending)
    
    tab1, tab2, tab3 = st.tabs(["📋 My Tasks", "💬 Comments", "📊 My Progress"])
    
    with tab1:
        st.subheader("📋 My Assigned Tasks")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Start Next Task", use_container_width=True):
                pass
        with col2:
            status_filter = st.selectbox("📊 Filter by Status", ["All", "pending", "in_progress", "completed"])
        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        params = {}
        if status_filter != "All":
            params["status"] = status_filter
        
        response = make_request("GET", "/tasks", params=params)
        if response and response.status_code == 200:
            tasks = response.json()
            my_tasks = [t for t in tasks if t.get('assignee_id') == st.session_state.user_info.get('id')]
            
            if my_tasks:
                for task in my_tasks:
                    with st.container():
                        priority_colors = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                        status_colors = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
                        
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"### {priority_colors.get(task['priority'], '🔵')} {task['title']}")
                            st.markdown(f"{status_colors.get(task['status'], '📋')} **{task['status'].replace('_', ' ').title()}** | Priority: **{task['priority'].title()}**")
                            
                            if task.get('description'):
                                with st.expander("📝 Description"):
                                    st.write(task['description'])
                            
                            if task.get('deadline'):
                                deadline = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
                                days_left = (deadline.date() - date.today()).days
                                if days_left < 0:
                                    st.error(f"⚠️ Overdue by {abs(days_left)} days")
                                elif days_left == 0:
                                    st.warning("🚨 Due Today!")
                                elif days_left <= 3:
                                    st.warning(f"⏰ Due in {days_left} days")
                                else:
                                    st.info(f"📅 Due in {days_left} days")
                        
                        with col2:
                            current_status = task['status']
                            status_options = ["pending", "in_progress", "completed"]
                            current_index = status_options.index(current_status)
                            
                            new_status = st.selectbox(
                                "Update Status",
                                status_options,
                                index=current_index,
                                key=f"status_user_{task['id']}"
                            )
                            
                            if new_status != current_status:
                                if st.button("💾 Update", key=f"update_user_{task['id']}"):
                                    with st.spinner("Updating..."):
                                        response = make_request("PUT", f"/tasks/{task['id']}", {"status": new_status})
                                        if response and response.status_code == 200:
                                            st.success("✅ Status updated!")
                                            st.rerun()
                        
                        with col3:
                            if task['status'] == 'completed':
                                st.progress(1.0)
                                st.write("✅ 100%")
                            elif task['status'] == 'in_progress':
                                st.progress(0.5)
                                st.write("🔄 50%")
                            else:
                                st.progress(0.0)
                                st.write("⏳ 0%")
                        
                        st.divider()
            else:
                st.info("📝 No tasks assigned to you. Check with your admin for new assignments!")
    
    with tab2:
        st.subheader("💬 Task Comments")

        response = make_request("GET", "/tasks")
        if response and response.status_code == 200:
            tasks = response.json()
            my_tasks = [t for t in tasks if t.get('assignee_id') == st.session_state.user_info.get('id')]
            
            if my_tasks:
                task_options = {f"{t['title']} (ID: {t['id']})": t['id'] for t in my_tasks}
                selected_task = st.selectbox("📋 Select Task", list(task_options.keys()))
                task_id = task_options.get(selected_task)
                
                if task_id:
                    st.subheader("💬 Existing Comments")
                    comments_response = make_request("GET", f"/tasks/{task_id}/comments")
                    if comments_response and comments_response.status_code == 200:
                        comments = comments_response.json()
                        if comments:
                            for comment in comments:
                                with st.container():
                                    is_my_comment = comment['author_id'] == st.session_state.user_info.get('id')
                                    author_emoji = "👤" if is_my_comment else "👥"
                                    author_text = "You" if is_my_comment else f"User {comment['author_id']}"
                                    
                                    st.markdown(f"**{author_emoji} {author_text}** - 📅 {comment['created_at']}")
                                    
                                    if is_my_comment:
                                        st.info(f"💬 {comment['content']}")
                                    else:
                                        st.write(f"💬 {comment['content']}")
                                    st.divider()
                        else:
                            st.info("💬 No comments yet. Be the first to comment!")
                    
                    st.subheader("➕ Add New Comment")
                    with st.form("add_comment", clear_on_submit=True):
                        comment_content = st.text_area("💬 Your Comment", placeholder="Share an update, ask a question, or provide feedback...", height=100)
                        
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            submit = st.form_submit_button("📝 Add Comment", use_container_width=True)
                        
                        if submit and comment_content:
                            with st.spinner("Adding comment..."):
                                response = make_request("POST", "/comments", {
                                    "content": comment_content,
                                    "task_id": task_id
                                })
                                if response and response.status_code == 200:
                                    st.success("✅ Comment added!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to add comment")
                        elif submit:
                            st.warning("⚠️ Please enter a comment")
            else:
                st.info("📝 No tasks available for commenting")
    
    with tab3:
        st.subheader("📊 My Progress Analytics")

        response = make_request("GET", "/tasks")
        if response and response.status_code == 200:
            tasks = response.json()
            my_tasks = [t for t in tasks if t.get('assignee_id') == st.session_state.user_info.get('id')]
            
            if my_tasks:
                df = pd.DataFrame(my_tasks)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    status_counts = df['status'].value_counts()
                    fig = px.pie(values=status_counts.values, names=status_counts.index, 
                               title="My Task Status Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    priority_counts = df['priority'].value_counts()
                    colors = ['green' if p == 'low' else 'orange' if p == 'medium' else 'red' 
                             for p in priority_counts.index]
                    fig = px.bar(x=priority_counts.index, y=priority_counts.values,
                               title="My Task Priority Distribution",
                               color=priority_counts.index,
                               color_discrete_map={'low': 'green', 'medium': 'orange', 'high': 'red'})
                    st.plotly_chart(fig, use_container_width=True)
                
                if 'created_at' in df.columns:
                    df['created_date'] = pd.to_datetime(df['created_at']).dt.date
                    df_sorted = df.sort_values('created_date')
                    
                    fig = px.timeline(df_sorted, x_start='created_date', x_end='created_date', 
                                    y='title', color='status',
                                    title="My Task Timeline")
                    st.plotly_chart(fig, use_container_width=True)
                
                completed_tasks = len(df[df['status'] == 'completed'])
                total_tasks = len(df)
                completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
                
                st.metric("📈 Completion Rate", f"{completion_rate:.1f}%")
                st.progress(completion_rate / 100)
                
            else:
                st.info("📊 No task data available for analytics")

def main():
    st.set_page_config(
        page_title="Team Task Management", 
        page_icon="📋", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stButton > button {
        border-radius: 10px;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stExpander {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    .task-card {
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.session_state.token and st.session_state.user_info:
        with st.sidebar:
            st.markdown("### 👤 User Profile")
            st.markdown(f"**Username:** {st.session_state.user_info['username']}")
            st.markdown(f"**Email:** {st.session_state.user_info.get('email', 'N/A')}")
            st.markdown(f"**Role:** {st.session_state.user_info['role'].title()}")
            
            st.divider()
            
            st.markdown("### ⚡ Quick Actions")
            if st.button("🔄 Refresh Dashboard", use_container_width=True):
                st.rerun()
            
            if st.button("🌙 Toggle Theme", use_container_width=True):
                st.info("Theme toggle coming soon!")
            
            st.divider()

            if st.button("🚪 Logout", use_container_width=True, type="primary"):
                st.session_state.token = None
                st.session_state.user_info = None
                st.session_state.clear()  
                st.success("👋 Logged out successfully!")
                st.rerun()

            st.markdown("---")
            st.markdown("### ℹ️ System Info")
            st.markdown(f"**API Status:** {'🟢 Connected' if st.session_state.token else '🔴 Disconnected'}")
            st.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
    
    if not st.session_state.token:
        login_page()
    else:
        notification_container = st.container()
        
        try:
            if st.session_state.user_info['role'] == 'admin':
                admin_dashboard()
            else:
                user_dashboard()
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("🔄 Please try refreshing the page or contact your administrator.")
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 14px;'>"
        "📋 Team Task Management System | Built with Streamlit"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()