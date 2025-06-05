"""
MCP Continuity Service - Streamlit Frontend
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

# Configure page
st.set_page_config(
    page_title="MCP Continuity Service",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

class MCPContinuityApp:
    def __init__(self):
        self.api_base = "http://localhost:8000/api"
        
    def main(self):
        st.title("🔄 MCP Continuity Service")
        st.markdown("Professional continuity service for LLMs with MCP integration")
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choose a page:",
            ["Dashboard", "Chat Interface", "Projects", "Sessions", "Settings"]
        )
        
        if page == "Dashboard":
            self.dashboard_page()
        elif page == "Chat Interface":
            self.chat_page()
        elif page == "Projects":
            self.projects_page()
        elif page == "Sessions":
            self.sessions_page()
        elif page == "Settings":
            self.settings_page()
    
    def dashboard_page(self):
        """Main dashboard"""
        st.header("📊 Dashboard")
        
        # Service status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if self.check_api_health():
                st.metric("API Status", "🟢 Online")
            else:
                st.metric("API Status", "🔴 Offline")
        
        with col2:
            st.metric("Active Sessions", "3")
        
        with col3:
            st.metric("Active Projects", "5")
        
        with col4:
            st.metric("Critical Missions", "1")
        
        st.divider()
        
        # Recent activity
        st.subheader("Recent Activity")
        
        # Mock data for now
        activity_data = [
            {"Time": "10:30", "Session": "dev-session-1", "Action": "Context recovery", "Status": "✅"},
            {"Time": "10:25", "Session": "analysis-session", "Action": "Emergency backup", "Status": "✅"},
            {"Time": "10:20", "Session": "dev-session-1", "Action": "Input preservation", "Status": "✅"},
        ]
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True)

    def chat_page(self):
        """Chat interface"""
        st.header("💬 Chat with Continuity")
        
        # Initialize session state
        if "session_id" not in st.session_state:
            st.session_state.session_id = f"streamlit-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if message.get("metadata"):
                    with st.expander("Details"):
                        st.json(message["metadata"])
        
        # Chat input
        if prompt := st.chat_input("Digite sua mensagem..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)
            
            # Process via API
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    response = self.process_user_input(prompt, st.session_state.session_id)
                    
                    if response:
                        if response.get("type") == "continuity_response":
                            st.write("🔄 **Context Recovery Completed**")
                            
                            if response.get("projects"):
                                st.write("**Active Projects:**")
                                for project in response["projects"]:
                                    st.write(f"- {project}")
                            
                            if response.get("critical_missions"):
                                st.write("**Critical Missions:**")
                                for mission in response["critical_missions"]:
                                    st.write(f"- {mission}")
                            
                            if response.get("summary"):
                                st.info(response["summary"])
                        
                        else:
                            st.write("Session continuing normally...")
                        
                        # Add assistant response
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response.get("summary", "Response processed"),
                            "metadata": response
                        })
                    else:
                        st.error("Failed to get response from API")

    def projects_page(self):
        """Projects management page"""
        st.header("📁 Projects Management")
        
        # Project creation section
        st.subheader("➕ Create New Project")
        with st.form("create_project"):
            col1, col2 = st.columns(2)
            with col1:
                project_name = st.text_input("Project Name", placeholder="e.g., luaraujo-app")
                project_type = st.selectbox("Project Type", [
                    "Mobile App", "Web App", "API Service", "Data Analysis", 
                    "Documentation", "Research", "Other"
                ])
            with col2:
                project_description = st.text_area("Description", placeholder="Brief project description...")
                project_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            
            submitted = st.form_submit_button("Create Project")
            if submitted and project_name:
                st.success(f"✅ Project '{project_name}' created successfully!")
                st.rerun()
        
        st.divider()
        
        # Active projects list
        st.subheader("📋 Active Projects")
        
        # Mock project data (in real implementation, this would come from API)
        projects_data = [
            {
                "Name": "luaraujo", 
                "Type": "Mobile App", 
                "Status": "🟢 Active",
                "Priority": "High",
                "Last Update": "2025-05-28 13:44",
                "Progress": 85,
                "Next Action": "CORREÇÃO NESTED SCROLL"
            },
            {
                "Name": "luaraujo-premium-hub", 
                "Type": "Web App", 
                "Status": "⏸️ Paused",
                "Priority": "Medium", 
                "Last Update": "2025-05-28 13:44",
                "Progress": 70,
                "Next Action": "Aguardando VPS"
            },
            {
                "Name": "mcp-continuity-service", 
                "Type": "API Service", 
                "Status": "🟢 Active",
                "Priority": "Critical",
                "Last Update": "2025-05-28 18:45",
                "Progress": 90,
                "Next Action": "Auth implementation"
            }
        ]

        for i, project in enumerate(projects_data):
            with st.expander(f"🗂️ {project['Name']} - {project['Status']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Progress", f"{project['Progress']}%")
                    st.progress(project['Progress'] / 100)
                
                with col2:
                    st.write(f"**Type:** {project['Type']}")
                    st.write(f"**Priority:** {project['Priority']}")
                    st.write(f"**Last Update:** {project['Last Update']}")
                
                with col3:
                    st.write(f"**Next Action:**")
                    st.info(project['Next Action'])
                
                # Project actions
                action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                with action_col1:
                    if st.button(f"▶️ Resume", key=f"resume_{i}"):
                        st.success(f"Resumed project: {project['Name']}")
                
                with action_col2:
                    if st.button(f"⏸️ Pause", key=f"pause_{i}"):
                        st.warning(f"Paused project: {project['Name']}")
                
                with action_col3:
                    if st.button(f"📊 Details", key=f"details_{i}"):
                        st.info("Project details would open in sidebar")
                
                with action_col4:
                    if st.button(f"🗑️ Archive", key=f"archive_{i}"):
                        st.error(f"Archived project: {project['Name']}")
        
        # Project statistics
        st.divider()
        st.subheader("📈 Project Statistics")
        
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        with stats_col1:
            st.metric("Total Projects", len(projects_data))
        with stats_col2:
            active_count = sum(1 for p in projects_data if "Active" in p["Status"])
            st.metric("Active Projects", active_count)
        with stats_col3:
            avg_progress = sum(p["Progress"] for p in projects_data) / len(projects_data)
            st.metric("Average Progress", f"{avg_progress:.1f}%")
        with stats_col4:
            critical_count = sum(1 for p in projects_data if p["Priority"] == "Critical")
            st.metric("Critical Projects", critical_count)

    def sessions_page(self):
        """Sessions management page"""
        st.header("🔄 Sessions Management")
        
        # Session filters
        st.subheader("🔍 Session Filters")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            session_status = st.selectbox("Status", ["All", "Active", "Paused", "Completed", "Emergency"])
        with filter_col2:
            session_type = st.selectbox("Type", ["All", "Development", "Analysis", "Recovery", "Chat"])
        with filter_col3:
            date_range = st.selectbox("Date Range", ["Today", "This Week", "This Month", "All Time"])
        
        st.divider()
        
        # Active sessions
        st.subheader("⚡ Active Sessions")
        
        active_sessions = [
            {
                "ID": "dev-session-1",
                "Project": "luaraujo",
                "Type": "Development",
                "Status": "🟢 Active",
                "Started": "2025-05-28 10:30",
                "Duration": "8h 15m",
                "Last Activity": "2 minutes ago",
                "Messages": 127
            },
            {
                "ID": "analysis-session",
                "Project": "mcp-continuity-service", 
                "Type": "Analysis",
                "Status": "🟡 Paused",
                "Started": "2025-05-28 14:20",
                "Duration": "4h 25m", 
                "Last Activity": "1 hour ago",
                "Messages": 43
            }
        ]
        
        for i, session in enumerate(active_sessions):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{session['ID']}** - {session['Status']}")
                    st.write(f"Project: {session['Project']}")
                    st.caption(f"Type: {session['Type']}")
                
                with col2:
                    st.write(f"**Duration:** {session['Duration']}")
                    st.write(f"**Messages:** {session['Messages']}")
                
                with col3:
                    st.write(f"**Started:** {session['Started']}")
                    st.write(f"**Last Activity:** {session['Last Activity']}")
                
                with col4:
                    if st.button("📊", key=f"view_{i}", help="View Details"):
                        st.info(f"Opening details for {session['ID']}")
                    if st.button("⏸️", key=f"pause_{i}", help="Pause Session"):
                        st.warning(f"Paused {session['ID']}")
                    if st.button("🛑", key=f"stop_{i}", help="Stop Session"):
                        st.error(f"Stopped {session['ID']}")
                
                st.divider()

        # Session history
        st.subheader("📜 Session History")
        
        history_data = [
            {"Session ID": "backup-session-001", "Project": "luaraujo", "Type": "Emergency", "Status": "✅ Completed", "Duration": "15m", "Date": "2025-05-28"},
            {"Session ID": "dev-session-old", "Project": "premium-hub", "Type": "Development", "Status": "✅ Completed", "Duration": "6h 30m", "Date": "2025-05-27"},
            {"Session ID": "analysis-002", "Project": "continuity", "Type": "Analysis", "Status": "✅ Completed", "Duration": "2h 15m", "Date": "2025-05-27"},
        ]
        
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True)
        
        # Session statistics
        st.divider()
        st.subheader("📊 Session Statistics")
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric("Total Sessions", "47")
        with stat_col2:
            st.metric("Active Now", len(active_sessions))
        with stat_col3:
            st.metric("Avg Duration", "3h 42m")
        with stat_col4:
            st.metric("Success Rate", "94.3%")
        
        # Emergency controls
        st.divider()
        st.subheader("🚨 Emergency Controls")
        
        emergency_col1, emergency_col2, emergency_col3 = st.columns(3)
        with emergency_col1:
            if st.button("🛡️ Emergency Freeze All", type="secondary"):
                st.warning("All sessions frozen! Recovery tokens created.")
        
        with emergency_col2:
            if st.button("♻️ Auto Recovery", type="secondary"):
                st.info("Scanning for recoverable sessions...")
        
        with emergency_col3:
            if st.button("🧹 Clean Old Sessions", type="secondary"):
                st.success("Cleaned 3 old sessions (>7 days)")

    def settings_page(self):
        """Settings page"""
        st.header("⚙️ Settings")
        
        # API Configuration
        st.subheader("🔌 API Configuration")
        
        with st.form("api_settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                api_endpoint = st.text_input("API Endpoint", value="http://localhost:8000/api")
                timeout = st.number_input("Request Timeout (seconds)", min_value=5, max_value=120, value=30)
            
            with col2:
                retry_attempts = st.number_input("Retry Attempts", min_value=1, max_value=5, value=3)
                enable_debug = st.checkbox("Enable Debug Mode", value=False)
            
            if st.form_submit_button("Save API Settings"):
                st.success("✅ API settings saved successfully!")
        
        st.divider()
        
        # LLM Configuration
        st.subheader("🤖 LLM Configuration")
        
        with st.form("llm_settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                llm_provider = st.selectbox("LLM Provider", ["Anthropic", "OpenAI", "Local Ollama"])
                model_name = st.selectbox("Model", [
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307", 
                    "gpt-3.5-turbo",
                    "gpt-4"
                ])
            
            with col2:
                max_tokens = st.number_input("Max Tokens", min_value=100, max_value=4000, value=1000)
                temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
            
            api_key_input = st.text_input("API Key", type="password", placeholder="Enter your API key...")
            
            if st.form_submit_button("Save LLM Settings"):
                st.success("✅ LLM settings saved successfully!")
        
        st.divider()
        
        # Continuity Settings
        st.subheader("🔄 Continuity Settings")
        
        with st.form("continuity_settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                auto_backup = st.checkbox("Auto Backup", value=True)
                backup_interval = st.selectbox("Backup Interval", ["5 minutes", "15 minutes", "30 minutes", "1 hour"])
                max_backups = st.number_input("Max Backups to Keep", min_value=5, max_value=50, value=10)
            
            with col2:
                context_window = st.number_input("Context Window Size", min_value=1000, max_value=10000, value=4000)
                smart_cleanup = st.checkbox("Smart Cleanup", value=True)
                emergency_mode = st.checkbox("Emergency Mode", value=False)
            
            if st.form_submit_button("Save Continuity Settings"):
                st.success("✅ Continuity settings saved successfully!")
        
        st.divider()
        
        # User Preferences
        st.subheader("👤 User Preferences")
        
        with st.form("user_preferences"):
            col1, col2 = st.columns(2)
            
            with col1:
                theme = st.selectbox("Theme", ["Auto", "Light", "Dark"])
                language = st.selectbox("Language", ["English", "Portuguese", "Spanish"])
                timezone = st.selectbox("Timezone", ["UTC", "America/Sao_Paulo", "America/New_York"])
            
            with col2:
                notifications = st.checkbox("Enable Notifications", value=True)
                email_reports = st.checkbox("Email Reports", value=False)
                analytics = st.checkbox("Share Analytics", value=True)
            
            if st.form_submit_button("Save User Preferences"):
                st.success("✅ User preferences saved successfully!")

        # System Information
        st.divider()
        st.subheader("ℹ️ System Information")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.info("**Version:** 1.0.0")
            st.info("**Build:** 2025.05.28")
        
        with info_col2:
            st.info("**API Status:** 🟢 Online")
            st.info("**Uptime:** 2h 34m")
        
        with info_col3:
            st.info("**Memory Usage:** 234 MB")
            st.info("**Active Connections:** 3")
        
        # Danger Zone
        st.divider()
        st.subheader("⚠️ Danger Zone")
        
        danger_col1, danger_col2 = st.columns(2)
        
        with danger_col1:
            if st.button("🗑️ Clear All Data", type="secondary"):
                st.error("⚠️ This will permanently delete all data!")
        
        with danger_col2:
            if st.button("🔄 Reset to Defaults", type="secondary"):
                st.warning("⚠️ This will reset all settings to default!")
    
    def check_api_health(self) -> bool:
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def process_user_input(self, user_input: str, session_id: str) -> Optional[Dict]:
        """Process user input via API"""
        try:
            response = requests.post(
                f"{self.api_base}/process-input",
                json={
                    "user_input": user_input,
                    "session_id": session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Is the service running?")
            return None
        except Exception as e:
            st.error(f"Error: {e}")
            return None

def main():
    app = MCPContinuityApp()
    app.main()

if __name__ == "__main__":
    main()
