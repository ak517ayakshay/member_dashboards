#stuff going inside schemas.py

class DashboardRequest(BaseModel):
    member_id: str
    time_range: TimeRange = Field(..., description="Time range for the data retrieval")
    vitals: Optional[List[str]] = None
    categories: Optional[List[str]] = None


# stuff going inside apc_apis.py
def get_dashboard_response(dashboard_request, provider_id=None):
    """
    Generate dashboard response for a member.
    
    Delegates to grafana_panel_utils.alyf_get_member_panels_for_all_vitals for iframe generation.
    """
    from src.common.grafana_panel_utils import alyf_get_member_panels_for_all_vitals
    
    member_record = ALYF_MEMBER_OPS.get(dashboard_request.member_id)
    
    df = AlyfTable("vitals_catalog").read(
        filters={"category": "!= subjective", "vital_name": "!= soap"},
        selected_columns=["vital_display_name"]
    )
    vitals = df["vital_display_name"].tolist() if not df.empty else []
    
    # Using existing function to generate panels
    return alyf_get_member_panels_for_all_vitals(
        member_record=member_record,
        vitals=vitals,
        start_time=dashboard_request.time_range.start_timestamp,
        end_time=dashboard_request.time_range.end_timestamp
    )



#stuff going inside router.py

@router.post("/member_dashboards")
async def get_dashboard(
    dashboard_request: DashboardRequest,
    provider_id: str = Depends(token_auth)
) -> Dict[str, Dict[str, str]]:
    """
    Get dashboard data for a member.
    """
    try:
        return get_dashboard_response(dashboard_request, provider_id)
    except Exception as e:
        ALYF_LOGGER.log("ERROR", f"Error generating dashboard for {dashboard_request.member_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating dashboard: {str(e)}"
        )