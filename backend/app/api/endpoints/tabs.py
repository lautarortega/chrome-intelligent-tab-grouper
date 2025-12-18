from fastapi import APIRouter, Depends
from typing import List
from app.schemas.tabs import Tab, TabGroup, GroupingResponse
from app.services.tab_grouper import TabGrouperService
from app.services.title_generator import TitleGeneratorService

router = APIRouter()

@router.post("/group", response_model=GroupingResponse)
async def group_tabs(
    tabs: List[Tab],
    grouper_service: TabGrouperService = Depends(TabGrouperService),
    title_service: TitleGeneratorService = Depends(TitleGeneratorService)
):
    results = grouper_service.group_tabs(tabs)
    
    final_groups = []
    for cluster_id, cluster_tabs in results['clusters'].items():
        title = title_service.generate_title(cluster_tabs)
        final_groups.append(TabGroup(
            cluster_id=cluster_id,
            title=title,
            tabs=cluster_tabs
        ))
        
    return GroupingResponse(
        groups=final_groups,
        unclustered_tabs=results['unclustered_tabs'],
        total_tabs=results['total_tabs'],
        num_clusters=results['num_clusters']
    )
