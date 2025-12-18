from pydantic import BaseModel
from typing import List, Optional

class Tab(BaseModel):
    id: str
    url: str
    title: str
    body: Optional[str] = None

class TabGroup(BaseModel):
    cluster_id: str
    title: Optional[str] = None
    tabs: List[Tab]

class GroupingResponse(BaseModel):
    groups: List[TabGroup]
    unclustered_tabs: List[Tab]
    total_tabs: int
    num_clusters: int
