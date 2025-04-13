import streamlit as st
from employee_db import EmployeeDatabase
from datetime import datetime
import pymongo

def show():
    """Export attendance records with safe field access"""
    st.header("Export Attendance Records")
    db = EmployeeDatabase()
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")
    
    if st.button("Generate Report"):
        # Convert dates to datetime objects
        start_datetime = datetime(start_date.year, start_date.month, start_date.day)
        end_datetime = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
        
        # Get attendance records
        records = list(db.attendance_collection.find({
            "timestamp": {
                "$gte": start_datetime,
                "$lte": end_datetime
            }
        }).sort("timestamp", pymongo.ASCENDING))
        
        if not records:
            st.warning("No attendance records found for selected date range!")
            return
            
        # Prepare report data with safe field access
        report_data = []
        for record in records:
            employee = db.collection.find_one({"militaryID": record["militaryID"]}) or {}
            report_data.append({
                "Date": record["timestamp"].strftime("%Y-%m-%d"),
                "Time": record["timestamp"].strftime("%H:%M"),
                "Rank": employee.get("rank", "N/A"),
                "Name": employee.get("fullname", "Unknown"),
                "Military ID": record["militaryID"],
                "Status": record["status"]
            })

        # Display report
        st.dataframe(report_data)
        
        # Generate full attendance report including absentees
        all_employees = db.get_all_employees()
        present_ids = {r["militaryID"] for r in records}
        
        # Add absent employees to report
        for emp in all_employees:
            if emp["militaryID"] not in present_ids:
                report_data.append({
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Time": "00:00",
                    "Rank": emp.get("rank", "N/A"),
                    "Name": emp.get("fullname", "Unknown"),
                    "Military ID": emp["militaryID"],
                    "Status": "Absent"
                })

        # Display report
        st.dataframe(report_data)
        
        # Export options
        import pandas as pd
        df = pd.DataFrame(report_data)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"attendance_report_{start_date}_{end_date}.csv",
            mime="text/csv",
            key='download-csv'
        )