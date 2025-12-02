import streamlit as st
import pandas as pd

def render_brand_input(key_prefix="onboard"):
    """
    Renders input for Organization Name and dynamic list of Brands.
    Returns a tuple (org_name, brands_list).
    """
    col1, col2 = st.columns([2, 1])
    with col1:
        org_name = st.text_input("Organization Name", key=f"{key_prefix}_org_name")
    
    st.subheader("Brands")
    
    # Initialize session state for brands if not exists
    if f"{key_prefix}_brands" not in st.session_state:
        st.session_state[f"{key_prefix}_brands"] = [""]

    brands = st.session_state[f"{key_prefix}_brands"]

    for i, brand in enumerate(brands):
        col_b1, col_b2 = st.columns([4, 1])
        with col_b1:
            brands[i] = st.text_input(f"Brand {i+1}", value=brand, key=f"{key_prefix}_brand_{i}")
        with col_b2:
            if i > 0: # Don't allow deleting the first brand input
                if st.button("🗑️", key=f"{key_prefix}_del_brand_{i}"):
                    brands.pop(i)
                    st.rerun()

    if st.button("Add Another Brand", key=f"{key_prefix}_add_brand"):
        brands.append("")
        st.rerun()
    
    # Filter out empty strings
    valid_brands = [b for b in brands if b.strip()]
    
    return org_name, valid_brands

def render_competitor_analysis_form(brand_name, key_prefix):
    st.markdown(f"#### Competitor Analysis for {brand_name}")
    
    # Brand Links
    with st.expander(f"Social Media Links for {brand_name}", expanded=True):
        st.text_input("Facebook", key=f"{key_prefix}_fb")
        st.text_input("Instagram", key=f"{key_prefix}_insta")
        st.text_input("Twitter (X)", key=f"{key_prefix}_twitter")
        st.text_input("TikTok", key=f"{key_prefix}_tiktok")
        st.text_input("LinkedIn", key=f"{key_prefix}_linkedin")
        st.text_input("YouTube", key=f"{key_prefix}_youtube")
        st.text_input("Website", key=f"{key_prefix}_website")

    # Competitors
    st.markdown("##### Competitors")
    if f"{key_prefix}_competitor_count" not in st.session_state:
        st.session_state[f"{key_prefix}_competitor_count"] = 1

    competitors = []
    for i in range(st.session_state[f"{key_prefix}_competitor_count"]):
        with st.expander(f"Competitor {i+1}", expanded=False):
            comp_name = st.text_input("Name", key=f"{key_prefix}_comp_{i}_name")
            comp_fb = st.text_input("Facebook", key=f"{key_prefix}_comp_{i}_fb")
            comp_insta = st.text_input("Instagram", key=f"{key_prefix}_comp_{i}_insta")
            comp_twitter = st.text_input("Twitter", key=f"{key_prefix}_comp_{i}_twitter")
            comp_tiktok = st.text_input("TikTok", key=f"{key_prefix}_comp_{i}_tiktok")
            comp_linkedin = st.text_input("LinkedIn", key=f"{key_prefix}_comp_{i}_linkedin")
            comp_youtube = st.text_input("YouTube", key=f"{key_prefix}_comp_{i}_youtube")
            comp_website = st.text_input("Website", key=f"{key_prefix}_comp_{i}_website")
            
            if comp_name:
                competitors.append({
                    "name": comp_name,
                    "socials": {
                        "facebook": comp_fb,
                        "instagram": comp_insta,
                        "twitter": comp_twitter,
                        "tiktok": comp_tiktok,
                        "linkedin": comp_linkedin,
                        "youtube": comp_youtube,
                        "website": comp_website
                    }
                })

    if st.button("Add Competitor", key=f"{key_prefix}_add_comp"):
        st.session_state[f"{key_prefix}_competitor_count"] += 1
        st.rerun()

    return {
        "brand_socials": {
            "facebook": st.session_state.get(f"{key_prefix}_fb"),
            "instagram": st.session_state.get(f"{key_prefix}_insta"),
            "twitter": st.session_state.get(f"{key_prefix}_twitter"),
            "tiktok": st.session_state.get(f"{key_prefix}_tiktok"),
            "linkedin": st.session_state.get(f"{key_prefix}_linkedin"),
            "youtube": st.session_state.get(f"{key_prefix}_youtube"),
            "website": st.session_state.get(f"{key_prefix}_website"),
        },
        "competitors": competitors
    }

def render_google_trends_form(brand_name, key_prefix):
    st.markdown(f"#### Google Trends for {brand_name}")
    link = st.text_input("Google Trends Link", key=f"{key_prefix}_gtrends_link")
    search_terms = st.text_area("Search Terms (comma separated)", key=f"{key_prefix}_gtrends_terms")
    return {"link": link, "search_terms": search_terms}

def render_web_traffic_form(brand_name, competitors, key_prefix):
    st.markdown(f"#### Web Traffic for {brand_name}")
    st.info("Select 4 competitors from the list below (excluding the brand itself).")
    
    comp_names = [c['name'] for c in competitors]
    selected_comps = st.multiselect("Select Competitors", comp_names, max_selections=4, key=f"{key_prefix}_webtraffic_comps")
    
    return {"selected_competitors": selected_comps}

def render_social_listening_form(brand_name, competitors, key_prefix):
    st.markdown(f"#### Social Listening for {brand_name}")
    needs_listening = st.checkbox("Enable Social Listening", key=f"{key_prefix}_sl_enable")
    
    data = {"enabled": needs_listening}
    
    if needs_listening:
        # User requested to remove "Competitor Keyword Listening" and only keep Brand Health logic if needed
        # But the prompt said: "If Needed Selected Option to select “Competitor keyword listening” or “Brand Health” (one or both)"
        # AND "Don't give social listening selection option to Competitors."
        # So I will remove the selection for Competitor Keyword Listening and just show Brand Health inputs if enabled?
        # Or just remove the "Competitor Keyword Listening" option from the multiselect?
        # "Don't give social listening selection option to Competitors." implies removing that branch.
        
        st.subheader("Brand Health")
        
        # Keywords
        if f"{key_prefix}_keywords" not in st.session_state:
            st.session_state[f"{key_prefix}_keywords"] = []
        
        # Input for Keywords
        kw_col1, kw_col2 = st.columns([3, 1])
        with kw_col1:
            kw_input = st.text_input("Add Keyword", key=f"{key_prefix}_kw_input_field")
        with kw_col2:
            if st.button("Add Keyword", key=f"{key_prefix}_add_kw_btn"):
                if kw_input and len(st.session_state[f"{key_prefix}_keywords"]) < 10:
                    if kw_input not in st.session_state[f"{key_prefix}_keywords"]:
                        st.session_state[f"{key_prefix}_keywords"].append(kw_input)
                        st.session_state[f"{key_prefix}_kw_input_field"] = "" # Clear input
                        st.rerun()
                    else:
                        st.warning("Keyword already exists!")

        # Display Keywords Table
        if st.session_state[f"{key_prefix}_keywords"]:
            st.markdown("**Keywords List**")
            kw_df = pd.DataFrame(st.session_state[f"{key_prefix}_keywords"], columns=["Keywords"])
            st.table(kw_df)

        # Hashtags
        if f"{key_prefix}_hashtags" not in st.session_state:
            st.session_state[f"{key_prefix}_hashtags"] = []
            
        ht_col1, ht_col2 = st.columns([3, 1])
        with ht_col1:
            ht_input = st.text_input("Add Hashtag", key=f"{key_prefix}_ht_input_field")
        with ht_col2:
            if st.button("Add Hashtag", key=f"{key_prefix}_add_ht_btn"):
                if ht_input and len(st.session_state[f"{key_prefix}_hashtags"]) < 10:
                    if ht_input not in st.session_state[f"{key_prefix}_hashtags"]:
                        st.session_state[f"{key_prefix}_hashtags"].append(ht_input)
                        st.session_state[f"{key_prefix}_ht_input_field"] = "" # Clear input
                        st.rerun()
                    else:
                        st.warning("Hashtag already exists!")

        # Display Hashtags Table
        if st.session_state[f"{key_prefix}_hashtags"]:
            st.markdown("**Hashtags List**")
            ht_df = pd.DataFrame(st.session_state[f"{key_prefix}_hashtags"], columns=["Hashtags"])
            st.table(ht_df)
            
        data["brand_health"] = {
            "keywords": st.session_state[f"{key_prefix}_keywords"],
            "hashtags": st.session_state[f"{key_prefix}_hashtags"]
        }
            
    return data

def render_platform_access_form(brand_name, platform_name, key_prefix):
    st.markdown(f"#### {platform_name} Access for {brand_name}")
    details = st.text_area(f"Enter {platform_name} Access Details / Page Names", key=f"{key_prefix}_{platform_name}_details")
    return details
