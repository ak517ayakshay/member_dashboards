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
    member_record = ALYF_MEMBER_OPS.get(dashboard_request.member_id)
    
    df = AlyfTable("alyf_vitals").read(
        filters={"member_id": member_record["member_id"]},
        selected_columns=["vital_name"]
    )
    unique_vitals = df["vital_name"].unique().tolist()
    
    return alyf_get_member_panels_for_all_vitals(
        member_record=member_record,
        vitals=unique_vitals,
        start_time=dashboard_request.time_range.start_timestamp.replace(tzinfo=None),
        end_time=dashboard_request.time_range.end_timestamp.replace(tzinfo=None)
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
