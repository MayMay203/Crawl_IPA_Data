# from pydantic import BaseModel, Field

# class ResultSchema(BaseModel):
#     title: str = Field(description="The title of the workflow")
#     description: str = Field(description="The description of the workflow")
#     url: str = Field(description="The URL of the workflow")
#     name: str = Field(description="The name of the workflow") 

# from pydantic import BaseModel, Field
# from typing import List, Optional

# # Tin tức chung
# class NewsArticle(BaseModel):
#     title: str = Field(..., description="Tiêu đề bài viết")
#     summary: Optional[str] = Field(None, description="Tóm tắt nội dung bài viết")
#     url: str = Field(..., description="URL chi tiết bài viết")
#     publication_date: Optional[str] = Field(None, description="Ngày xuất bản")
#     category: Optional[str] = Field(None, description="Chuyên mục bài viết")

# # Cơ hội đầu tư
# class InvestmentOpportunity(BaseModel):
#     title: str = Field(..., description="Tên dự án đầu tư")
#     description: Optional[str] = Field(None, description="Thông tin chi tiết")
#     url: str = Field(..., description="Liên kết chi tiết")
#     sector: Optional[str] = Field(None, description="Ngành")
#     location: Optional[str] = Field(None, description="Địa điểm")
#     investment_amount: Optional[str] = Field(None, description="Vốn đầu tư")
#     contact_info: Optional[str] = Field(None, description="Thông tin liên hệ")

# # Chính sách đầu tư
# class InvestmentPolicy(BaseModel):
#     title: str = Field(..., description="Tên chính sách")
#     content: Optional[str] = Field(None, description="Nội dung chính sách")
#     url: str = Field(..., description="Link chi tiết")

# # Hướng dẫn đầu tư
# class InvestmentGuide(BaseModel):
#     title: str = Field(..., description="Tiêu đề hướng dẫn")
#     steps: Optional[str] = Field(None, description="Các bước hướng dẫn")
#     url: str = Field(..., description="Liên kết chi tiết")

# # Thông tin quy hoạch
# class PlanningInfo(BaseModel):
#     title: str = Field(..., description="Tên quy hoạch")
#     area: Optional[str] = Field(None, description="Khu vực")
#     description: Optional[str] = Field(None, description="Chi tiết quy hoạch")
#     url: str = Field(..., description="Liên kết chi tiết")

# # Chi phí đầu tư
# class InvestmentCost(BaseModel):
#     title: str = Field(..., description="Loại chi phí")
#     cost: Optional[str] = Field(None, description="Giá trị chi phí")
#     description: Optional[str] = Field(None, description="Mô tả")
#     url: str = Field(..., description="URL chi tiết nếu có")

# # Kết quả tổng hợp
# class ResultSchema(BaseModel):
#     news_articles: Optional[List[NewsArticle]] = Field(None, description="Danh sách bài viết tin tức")
#     investment_opportunities: Optional[List[InvestmentOpportunity]] = Field(None, description="Danh sách cơ hội đầu tư")
#     investment_policies: Optional[List[InvestmentPolicy]] = Field(None, description="Danh sách chính sách đầu tư")
#     investment_guides: Optional[List[InvestmentGuide]] = Field(None, description="Danh sách hướng dẫn đầu tư")
#     planning_infos: Optional[List[PlanningInfo]] = Field(None, description="Danh sách quy hoạch")
#     investment_costs: Optional[List[InvestmentCost]] = Field(None, description="Danh sách chi phí đầu tư")


from pydantic import BaseModel, Field
from typing import List, Optional

# Tin tức chung giữ nguyên
class NewsArticle(BaseModel):
    title: str = Field(..., description="Tiêu đề bài viết")
    summary: Optional[str] = Field(None, description="Tóm tắt nội dung bài viết")
    url: str = Field(..., description="URL chi tiết bài viết")
    publication_date: Optional[str] = Field(None, description="Ngày xuất bản")
    category: Optional[str] = Field(None, description="Chuyên mục bài viết")

# Thông tin liên hệ
class IPAContactInfoItem(BaseModel):
    title: str = Field(..., description="Tiêu đề thông tin liên hệ của IPA")
    description: str = Field(..., description="Nội dung mô tả tương ứng với tiêu đề")

# Lợi thế đầu tư
class InvestmentAdvantageItem(BaseModel):
    name: str = Field(..., description="Tên lợi thế đầu tư")
    url: str = Field(..., description="URL chi tiết của lợi thế đầu tư")

class InvestmentAdvantage(BaseModel):
    advantages: List[InvestmentAdvantageItem] = Field(..., description="Danh sách lợi thế đầu tư")

# Lĩnh vực thu hút đầu tư
class InvestmentAttractionField(BaseModel):
    name: str = Field(..., description="Tên lĩnh vực thu hút đầu tư")
    url: str = Field(..., description="URL file PDF chi tiết lĩnh vực")

class InvestmentAttraction(BaseModel):
    fields: List[InvestmentAttractionField] = Field(..., description="Danh sách các lĩnh vực thu hút đầu tư")

# Đầu tư tại Đà Nẵng - mục con có thể lồng nhau
class InvestmentAtDanangSubItem(BaseModel):
    title: str = Field(..., description="Tên mục con")
    url: str = Field(..., description="URL chi tiết của mục con")

class InvestmentAtDanangItem(BaseModel):
    title: str = Field(..., description="Tên mục chính")
    url: str = Field(..., description="URL chi tiết của mục chính")
    sub_items: Optional[List[InvestmentAtDanangSubItem]] = Field(None, description="Danh sách mục con")

class InvestmentAtDanang(BaseModel):
    items: List[InvestmentAtDanangItem] = Field(..., description="Danh sách các mục đầu tư tại Đà Nẵng")

# Kết quả tổng hợp mới, giữ lại Tin tức và Hướng dẫn đầu tư, thêm phần mới
class ResultSchema(BaseModel):
    news_articles: Optional[List[NewsArticle]] = Field(None, description="Danh sách bài viết tin tức")
    investment_advantages: Optional[InvestmentAdvantage] = Field(None, description="Lợi thế đầu tư")
    investment_attraction_fields: Optional[InvestmentAttraction] = Field(None, description="Lĩnh vực thu hút đầu tư")
    investment_at_danang: Optional[InvestmentAtDanang] = Field(None, description="Đầu tư tại Đà Nẵng")
    ipa_contact_info: Optional[List[IPAContactInfoItem]] = Field(None, description="Danh sách thông tin liên hệ của cơ quan IPA")


class SubItemSchema(BaseModel):
    title: str = Field(..., description="Tên mục chính")
    url: str = Field(..., description="URL chi tiết của mục chính")
