import streamlit as st
import json
import pandas as pd
import io
from utils import data_manager, ui_components

# Page Config
st.set_page_config(
    page_title="Client Success Onboarding",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .block-container {
        padding-top: 2rem;
    }
    #MainMenu {visibility: hidden; display: none;}
    footer {visibility: hidden; display: none;}
    /* header {visibility: hidden; display: none;} - Removed to keep sidebar toggle visible */
    </style>
    """, unsafe_allow_html=True)

def generate_excel(record):
    flat_data = []
    
    org = record.get("organization", "")
    exec_name = record.get("executive_name", "")
    rec_type = record.get("type", "")
    date = record.get("onboard_date") or record.get("presentation_date")
    reports_list = ", ".join(record.get("reports", []))

    for b in record.get("brands", []):
        brand_name = b.get("name", "")
        b_data = b.get("data", {})
        
        # Base row data
        base_row = {
            "Executive Name": exec_name,
            "Organization": org,
            "Type": rec_type,
            "Date": date,
            "Brand": brand_name,
            "Reports Selected": reports_list
        }
        
        # 1. Competitor Analysis
        comp_analysis = b_data.get("competitor_analysis", {})
        
        # Brand Socials
        brand_socials = comp_analysis.get("brand_socials", {})
        for platform, link in brand_socials.items():
            row = base_row.copy()
            row["Category"] = "Brand Socials"
            row["Sub-Category"] = platform.capitalize()
            row["Detail"] = link
            flat_data.append(row)
            
        # Competitors
        competitors = comp_analysis.get("competitors", [])
        for i, comp in enumerate(competitors):
            c_name = comp.get("name", f"Competitor {i+1}")
            c_socials = comp.get("socials", {})
            for platform, link in c_socials.items():
                row = base_row.copy()
                row["Category"] = "Competitor Analysis"
                row["Sub-Category"] = f"{c_name} - {platform.capitalize()}"
                row["Detail"] = link
                flat_data.append(row)

        # 2. Google Trends
        g_trends = b_data.get("google_trends", {})
        if g_trends:
            row = base_row.copy()
            row["Category"] = "Google Trends"
            row["Sub-Category"] = "Link"
            row["Detail"] = g_trends.get("link", "")
            flat_data.append(row)
            
            row = base_row.copy()
            row["Category"] = "Google Trends"
            row["Sub-Category"] = "Search Terms"
            row["Detail"] = g_trends.get("search_terms", "")
            flat_data.append(row)

        # 3. Web Traffic
        web_traffic = b_data.get("web_traffic", {})
        if web_traffic:
            selected_comps = web_traffic.get("selected_competitors", [])
            row = base_row.copy()
            row["Category"] = "Web Traffic"
            row["Sub-Category"] = "Selected Competitors"
            row["Detail"] = ", ".join(selected_comps)
            flat_data.append(row)

        # 4. Social Listening
        social_listening = b_data.get("social_listening", {})
        if social_listening.get("enabled"):
            brand_health = social_listening.get("brand_health", {})
            
            # Keywords
            keywords = brand_health.get("keywords", [])
            if keywords:
                row = base_row.copy()
                row["Category"] = "Social Listening"
                row["Sub-Category"] = "Keywords"
                row["Detail"] = ", ".join(keywords)
                flat_data.append(row)
                
            # Hashtags
            hashtags = brand_health.get("hashtags", [])
            if hashtags:
                row = base_row.copy()
                row["Category"] = "Social Listening"
                row["Sub-Category"] = "Hashtags"
                row["Detail"] = ", ".join(hashtags)
                flat_data.append(row)

        # 5. Platform Access (Meta, GA, etc.)
        # These are usually stored as direct keys in b_data if I recall correctly how ui_components returns them?
        # Let's check ui_components.py or how they are saved. 
        # In clients.py (previous version), they were saved as:
        # brand_data["meta_platform"] = ui_components.render_platform_access_form(...)
        
        platform_keys = ["meta_platform", "google_analytics", "meta_campaigns", "google_ads"]
        for pk in platform_keys:
            p_data = b_data.get(pk)
            if p_data:
                row = base_row.copy()
                row["Category"] = "Platform Access"
                row["Sub-Category"] = pk.replace("_", " ").title()
                row["Detail"] = p_data
                flat_data.append(row)

    if not flat_data:
        # If no detailed data, at least return the base info
        flat_data.append({
            "Executive Name": exec_name,
            "Organization": org,
            "Type": rec_type,
            "Date": date,
            "Brand": "",
            "Reports Selected": reports_list,
            "Category": "No Data",
            "Sub-Category": "",
            "Detail": ""
        })

    df = pd.DataFrame(flat_data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Detailed Data')
    
    return buffer

def main():
    st.title("🚀 Client Success Onboarding System")
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    options = ["Onboard Client", "Pitch Client", "Update Client", "Manage Clients", "Clients Details"]
    choice = st.sidebar.radio("Go to", options)

    if choice == "Onboard Client":
        st.header("Onboard New Client")
        
        # 1. Data Entry Executive Name (Compulsory)
        executive_name = st.text_input("Data Entry Executive Name *", key="onboard_exec_name")
        
        if executive_name:
            st.success(f"Executive: {executive_name}")
            
            # 2. Organization Name & Brands
            org_name, brands = ui_components.render_brand_input("onboard")
            
            if org_name:
                st.info(f"Organization: {org_name}")
                
                if brands and any(b.strip() for b in brands):
                    st.write(f"**Brands**: {', '.join([b for b in brands if b.strip()])}")
                    
                    report_options = [
                        "Competitor Analysis", "Google Trends", "Web Traffic", 
                        "Social Listening", "Meta Platform", "Google Analytics", 
                        "Meta Campaigns", "Google Ads"
                    ]
                    selected_reports = st.multiselect("Select Reports", report_options)
                    
                    # Container for all brand data
                    all_brand_data = {}
            
                    for brand in brands:
                        if not brand.strip():
                            continue
                            
                        st.markdown(f"---")
                        st.subheader(f"Details for Brand: {brand}")
                        brand_data = {}
                        
                        # Competitor Analysis
                        if "Competitor Analysis" in selected_reports:
                            brand_data["competitor_analysis"] = ui_components.render_competitor_analysis_form(brand, f"onboard_{brand}")
                            if brand_data["competitor_analysis"]:
                                with st.expander(f"View Entered Competitor Data for {brand}"):
                                    st.json(brand_data["competitor_analysis"])
                        
                        competitors = brand_data.get("competitor_analysis", {}).get("competitors", [])

                        if "Google Trends" in selected_reports:
                            brand_data["google_trends"] = ui_components.render_google_trends_form(brand, f"onboard_{brand}")
                            
                        if "Web Traffic" in selected_reports:
                            brand_data["web_traffic"] = ui_components.render_web_traffic_form(brand, competitors, f"onboard_{brand}")
                            
                        if "Social Listening" in selected_reports:
                            brand_data["social_listening"] = ui_components.render_social_listening_form(brand, competitors, f"onboard_{brand}")
                            
                        if "Meta Platform" in selected_reports:
                            brand_data["meta_platform"] = ui_components.render_platform_access_form(brand, "Meta Platform", f"onboard_{brand}")
                            
                        if "Google Analytics" in selected_reports:
                            brand_data["google_analytics"] = ui_components.render_platform_access_form(brand, "Google Analytics", f"onboard_{brand}")
                            
                        if "Meta Campaigns" in selected_reports:
                            brand_data["meta_campaigns"] = ui_components.render_platform_access_form(brand, "Meta Campaigns", f"onboard_{brand}")
                            
                        if "Google Ads" in selected_reports:
                            brand_data["google_ads"] = ui_components.render_platform_access_form(brand, "Google Ads", f"onboard_{brand}")

                        all_brand_data[brand] = brand_data

                    onboard_date = st.date_input("Client Onboard Date")
                    
                    if st.button("Save Data", type="primary"):
                        client_record = {
                            "executive_name": executive_name,
                            "organization": org_name,
                            "brands": [{"name": b, "data": all_brand_data.get(b, {})} for b in brands if b.strip()],
                            "reports": selected_reports,
                            "onboard_date": str(onboard_date),
                            "type": "onboard"
                        }
                        
                        data_manager.add_client_record(client_record)
                        st.success("Client Onboarded Successfully!")
                        st.json(client_record)
                        
                        excel_data = generate_excel(client_record)
                        st.download_button(
                            label="Download Excel",
                            data=excel_data,
                            file_name=f"{org_name}_onboard.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="onboard_download"
                        )
                else:
                    st.warning("Please add at least one Brand to proceed.")
            else:
                st.warning("Please enter Organization Name to proceed.")
        else:
            st.warning("Please enter Data Entry Executive Name to start.")

    elif choice == "Pitch Client":
        st.header("Pitch New Client")
        
        # 1. Data Entry Executive Name (Compulsory)
        executive_name = st.text_input("Data Entry Executive Name *", key="pitch_exec_name")
        
        if executive_name:
            st.success(f"Executive: {executive_name}")
            
            # 2. Organization & Brands
            org_name, brands = ui_components.render_brand_input("pitch")
            
            if org_name:
                st.info(f"Organization: {org_name}")
                
                if brands and any(b.strip() for b in brands):
                    st.write(f"**Brands**: {', '.join([b for b in brands if b.strip()])}")
                    
                    presentation_date = st.date_input("Client Presentation Date")
                    
                    # Restricted reports for Pitch
                    report_options = ["Competitor Analysis", "Social Listening"]
                    selected_reports = st.multiselect("Select Reports", report_options, key="pitch_reports")
                    
                    all_brand_data = {}
            
                    for brand in brands:
                        if not brand.strip():
                            continue
                            
                        st.markdown(f"---")
                        st.subheader(f"Details for Brand: {brand}")
                        brand_data = {}
                        
                        if "Competitor Analysis" in selected_reports:
                            brand_data["competitor_analysis"] = ui_components.render_competitor_analysis_form(brand, f"pitch_{brand}")
                            if brand_data["competitor_analysis"]:
                                with st.expander(f"View Entered Competitor Data for {brand}"):
                                    st.json(brand_data["competitor_analysis"])
                        
                        competitors = brand_data.get("competitor_analysis", {}).get("competitors", [])

                        if "Social Listening" in selected_reports:
                            brand_data["social_listening"] = ui_components.render_social_listening_form(brand, competitors, f"pitch_{brand}")

                        all_brand_data[brand] = brand_data

                    if st.button("Save Pitch Data", type="primary"):
                        client_record = {
                            "executive_name": executive_name,
                            "organization": org_name,
                            "brands": [{"name": b, "data": all_brand_data.get(b, {})} for b in brands if b.strip()],
                            "reports": selected_reports,
                            "presentation_date": str(presentation_date),
                            "type": "pitch"
                        }
                        
                        data_manager.add_client_record(client_record)
                        st.success("Pitch Data Saved Successfully!")
                        st.json(client_record)
                        
                        excel_data = generate_excel(client_record)
                        st.download_button(
                            label="Download Excel",
                            data=excel_data,
                            file_name=f"{org_name}_pitch.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="pitch_download"
                        )
                else:
                    st.warning("Please add at least one Brand to proceed.")
            else:
                st.warning("Please enter Organization Name to proceed.")
        else:
            st.warning("Please enter Data Entry Executive Name to start.")

    elif choice == "Update Client":
        st.header("Update Existing Client (Add Brand)")
        
        orgs = data_manager.get_all_organizations()
        selected_org = st.selectbox("Select Organization", [""] + orgs, key="update_org_select")
        
        if selected_org:
            st.subheader(f"Add New Brand to {selected_org}")
            
            # Reuse brand input logic but we only need brands, not org name
            # We can manually implement the brand list input here for simplicity or modify ui_components
            # Let's implement a simple version here since we know the org
            
            if "update_brands" not in st.session_state:
                st.session_state["update_brands"] = [""]
                
            brands = st.session_state["update_brands"]
            
            for i, brand in enumerate(brands):
                col_b1, col_b2 = st.columns([4, 1])
                with col_b1:
                    brands[i] = st.text_input(f"New Brand {i+1}", value=brand, key=f"update_brand_{i}")
                with col_b2:
                    if i > 0:
                        if st.button("🗑️", key=f"update_del_brand_{i}"):
                            brands.pop(i)
                            st.rerun()

            if st.button("Add Another Brand", key="update_add_brand"):
                brands.append("")
                st.rerun()
            
            valid_brands = [b for b in brands if b.strip()]
            
            report_options = [
                "Competitor Analysis", "Google Trends", "Web Traffic", 
                "Social Listening", "Meta Platform", "Google Analytics", 
                "Meta Campaigns", "Google Ads"
            ]
            selected_reports = st.multiselect("Select Reports", report_options, key="update_reports")
            
            all_brand_data = {}
            
            if valid_brands:
                for brand in valid_brands:
                    st.markdown(f"---")
                    st.subheader(f"Details for Brand: {brand}")
                    brand_data = {}
                    
                    if "Competitor Analysis" in selected_reports:
                        brand_data["competitor_analysis"] = ui_components.render_competitor_analysis_form(brand, f"update_{brand}")
                    
                    competitors = brand_data.get("competitor_analysis", {}).get("competitors", [])

                    if "Google Trends" in selected_reports:
                        brand_data["google_trends"] = ui_components.render_google_trends_form(brand, f"update_{brand}")
                        
                    if "Web Traffic" in selected_reports:
                        brand_data["web_traffic"] = ui_components.render_web_traffic_form(brand, competitors, f"update_{brand}")
                        
                    if "Social Listening" in selected_reports:
                        brand_data["social_listening"] = ui_components.render_social_listening_form(brand, competitors, f"update_{brand}")
                        
                    if "Meta Platform" in selected_reports:
                        brand_data["meta_platform"] = ui_components.render_platform_access_form(brand, "Meta Platform", f"update_{brand}")
                        
                    if "Google Analytics" in selected_reports:
                        brand_data["google_analytics"] = ui_components.render_platform_access_form(brand, "Google Analytics", f"update_{brand}")
                        
                    if "Meta Campaigns" in selected_reports:
                        brand_data["meta_campaigns"] = ui_components.render_platform_access_form(brand, "Meta Campaigns", f"update_{brand}")
                        
                    if "Google Ads" in selected_reports:
                        brand_data["google_ads"] = ui_components.render_platform_access_form(brand, "Google Ads", f"update_{brand}")

                    all_brand_data[brand] = brand_data

            if st.button("Save New Brands", type="primary", key="update_save"):
                if not valid_brands:
                    st.error("Please add at least one brand.")
                else:
                    record = data_manager.get_record_by_org(selected_org)
                    if record:
                        for brand, data in all_brand_data.items():
                            record["brands"].append({
                                "name": brand,
                                "data": data
                            })
                        data_manager.update_client_record(record)
                        st.success(f"Added {len(valid_brands)} brands to {selected_org}!")
                        
                        # Display updated data in table
                        st.subheader("Updated Client Data")
                        flat_data = []
                        for b in record.get("brands", []):
                            flat_data.append({
                                "Brand": b.get("name"),
                                "Reports": ", ".join(selected_reports) if b.get("name") in valid_brands else "Existing"
                            })
                        st.table(pd.DataFrame(flat_data))
                        
                        # Excel Export
                        excel_data = generate_excel(record)
                        st.download_button(
                            label="Download Excel",
                            data=excel_data,
                            file_name=f"{selected_org}_updated.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="update_download"
                        )
                    else:
                        st.error("Organization record not found.")

    elif choice == "Manage Clients":
        st.header("Manage Existing Clients")
        
        orgs = data_manager.get_all_organizations()
        selected_org = st.selectbox("Select Organization", [""] + orgs)
        
        if selected_org:
            record = data_manager.get_record_by_org(selected_org)
            if record:
                # Filter brands for this org
                brand_names = [b["name"] for b in record.get("brands", [])]
                selected_brand = st.selectbox("Select Brand to Edit", [""] + brand_names)
                
                if selected_brand:
                    st.info(f"Editing data for {selected_brand} (Organization: {selected_org})")
                    
                    # Find the specific brand data
                    brand_data_entry = next((b for b in record["brands"] if b["name"] == selected_brand), None)
                    
                    if brand_data_entry:
                        data = brand_data_entry.get("data", {})
                        
                        # We need to flatten the data or present it in sections for editing
                        # Since the structure is complex, we can offer specific sections to edit
                        
                        edit_options = ["Competitor Analysis", "Google Trends", "Web Traffic", "Social Listening", "Platform Access"]
                        section_to_edit = st.selectbox("Select Section to Edit", edit_options)
                        
                        updated = False
                        
                        if section_to_edit == "Competitor Analysis":
                            comp_data = data.get("competitor_analysis", {})
                            
                            st.subheader("Brand Socials")
                            # Edit Brand Socials using text inputs (boxes)
                            socials = comp_data.get("brand_socials", {})
                            new_socials = {}
                            
                            col_s1, col_s2 = st.columns(2)
                            social_platforms = ["facebook", "instagram", "twitter", "tiktok", "linkedin", "youtube", "website"]
                            
                            for i, platform in enumerate(social_platforms):
                                current_val = socials.get(platform, "")
                                with (col_s1 if i % 2 == 0 else col_s2):
                                    new_socials[platform] = st.text_input(f"{platform.capitalize()}", value=current_val, key=f"edit_brand_{platform}")
                            
                            st.subheader("Competitors")
                            # Edit Competitors
                            competitors = comp_data.get("competitors", [])
                            # Flatten for editor
                            flat_comps = []
                            for c in competitors:
                                row = {"name": c.get("name")}
                                row.update(c.get("socials", {}))
                                flat_comps.append(row)
                            
                            comps_df = pd.DataFrame(flat_comps)
                            st.info("Edit Competitor details in the table below. Add new rows for new competitors.")
                            edited_comps = st.data_editor(comps_df, key="edit_competitors", num_rows="dynamic", use_container_width=True)
                            
                            if st.button("Save Competitor Analysis Changes"):
                                # Reconstruct data
                                new_comps = []
                                for index, row in edited_comps.iterrows():
                                    if row.get("name"):
                                        c_data = {"name": row["name"], "socials": {k: v for k, v in row.items() if k != "name"}}
                                        new_comps.append(c_data)
                                
                                if "competitor_analysis" not in data:
                                    data["competitor_analysis"] = {}
                                data["competitor_analysis"]["brand_socials"] = new_socials
                                data["competitor_analysis"]["competitors"] = new_comps
                                updated = True

                        elif section_to_edit == "Google Trends":
                            gt_data = data.get("google_trends", {})
                            link = st.text_input("Link", value=gt_data.get("link", ""))
                            terms = st.text_area("Search Terms", value=gt_data.get("search_terms", ""))
                            
                            if st.button("Save Google Trends Changes"):
                                data["google_trends"] = {"link": link, "search_terms": terms}
                                updated = True

                        elif section_to_edit == "Web Traffic":
                            wt_data = data.get("web_traffic", {})
                            # Just edit selected competitors list
                            current_comps = pd.DataFrame(wt_data.get("selected_competitors", []), columns=["Competitor"])
                            edited_wt = st.data_editor(current_comps, key="edit_web_traffic", num_rows="dynamic")
                            
                            if st.button("Save Web Traffic Changes"):
                                data["web_traffic"] = {"selected_competitors": edited_wt["Competitor"].tolist()}
                                updated = True

                        elif section_to_edit == "Social Listening":
                            sl_data = data.get("social_listening", {})
                            enabled = st.checkbox("Enabled", value=sl_data.get("enabled", False))
                            
                            bh_data = sl_data.get("brand_health", {})
                            
                            st.subheader("Keywords")
                            kw_df = pd.DataFrame(bh_data.get("keywords", []), columns=["Keyword"])
                            edited_kw = st.data_editor(kw_df, key="edit_sl_keywords", num_rows="dynamic")
                            
                            st.subheader("Hashtags")
                            ht_df = pd.DataFrame(bh_data.get("hashtags", []), columns=["Hashtag"])
                            edited_ht = st.data_editor(ht_df, key="edit_sl_hashtags", num_rows="dynamic")
                            
                            if st.button("Save Social Listening Changes"):
                                data["social_listening"] = {
                                    "enabled": enabled,
                                    "brand_health": {
                                        "keywords": edited_kw["Keyword"].tolist(),
                                        "hashtags": edited_ht["Hashtag"].tolist()
                                    }
                                }
                                updated = True
                        
                        elif section_to_edit == "Platform Access":
                            # Simple text areas for each platform
                            platforms = ["meta_platform", "google_analytics", "meta_campaigns", "google_ads"]
                            
                            new_platform_data = {}
                            for p in platforms:
                                val = data.get(p, "")
                                new_val = st.text_area(f"{p.replace('_', ' ').title()}", value=val, key=f"edit_{p}")
                                new_platform_data[p] = new_val
                            
                            if st.button("Save Platform Access Changes"):
                                for p, v in new_platform_data.items():
                                    data[p] = v
                                updated = True

                        if updated:
                            data_manager.update_client_record(record)
                            st.success("Data updated successfully!")
                            st.rerun()
                        
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        with col2:
                            if st.button("Delete Brand", type="primary"):
                                record["brands"] = [b for b in record["brands"] if b["name"] != selected_brand]
                                data_manager.update_client_record(record)
                                st.success(f"Brand {selected_brand} deleted.")
                                st.rerun()

                st.markdown("---")
                if st.button("Delete Entire Organization Record", type="primary"):
                    data_manager.delete_client_record(record["id"])
                    st.success(f"Organization {selected_org} deleted.")
                    st.rerun()
                
                # Excel Export for the managed client
                st.markdown("---")
                excel_data = generate_excel(record)
                st.download_button(
                    label="Download Client Data (Excel)",
                    data=excel_data,
                    file_name=f"{selected_org}_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="manage_download"
                )

    elif choice == "Clients Details":
        st.header("Client Data Overview")
        
        data = data_manager.load_data()
        
        if data:
            # Flatten data for display
            flat_data = []
            for r in data:
                for b in r.get("brands", []):
                    flat_data.append({
                        "Organization": r.get("organization"),
                        "Type": r.get("type"),
                        "Date": r.get("onboard_date") or r.get("presentation_date"),
                        "Brand": b.get("name"),
                        "Reports": ", ".join(r.get("reports", []))
                    })
            
            df = pd.DataFrame(flat_data)
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Export to CSV",
                csv,
                "clients_data.csv",
                "text/csv",
                key='download-csv'
            )
            
            # Excel export requires openpyxl
            # buffer = io.BytesIO()
            # with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            #     df.to_excel(writer, index=False)
            # st.download_button(
            #     "Export to Excel",
            #     buffer,
            #     "clients_data.xlsx",
            #     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            #     key='download-excel'
            # )
            
        else:
            st.info("No data available.")

if __name__ == "__main__":
    main()
