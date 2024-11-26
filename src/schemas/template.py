from pydantic import ConfigDict, field_validator

from src.schemas.format import GlobalResponseModel
from src.settings import BaseSchema


###### 생성 #######
class TemplateCreateRequest(BaseSchema):
    type: str
    description: str
    bag_file_path: str
    topics: str

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "type": "A",
                "description": "템플릿A 입니다~~~",
                "bagFilePath": "blah/blah/blah",
                "topics": "topics"
            }
        }
    }

class TemplateCreateResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    template_id: int
    type: str
    description: str
    bag_file_path: str
    topics: str
    created_at : str

    @field_validator('created_at', mode='before')
    def format_datetime(cls, value):
        return str(value)

class TemplateCreateResponseModel(GlobalResponseModel):
    model_config = {
        "json_schema_extra": {
            "example":
            {
                "statusCode": 201,
                "data": {
                    "templateId": 1,
                    "type": "A",
                    "description": "템플릿A 입니다~~~",
                    "bagFilePath": "blah/blah/blah",
                    "topics": "topics",
                    "createdAt": "2024-11-26 14:13:31.409721"
                },
                "message": "템플릿 생성 성공"
            }
        }
    }
    pass


###### 목록 조회 #######
class TemplateListResponse(BaseSchema):
    template_id: int
    template_type: str
    template_description: str

class TemplateListResponseModel(GlobalResponseModel):
    model_config = {
        "json_schema_extra": {
            "example":
                {
                    "statusCode": 200,
                    "data": [
                        {
                            "templateId": 1,
                            "templateType": "A",
                            "templateDescription": "템플릿A 입니다~~~"
                        }
                    ],
                    "message": "템플릿 목록 조회"
                }
        }
    }

    pass


###### 삭제 #######
class TemplateDeleteResponse(BaseSchema):
    template_id: int

class TemplateDeleteResponseModel(GlobalResponseModel):
    model_config = {
        "json_schema_extra": {
            "example":
                {
                    "statusCode": 200,
                    "data": [
                        {
                            "templateId": 1
                        }
                    ],
                    "message": "템플릿 삭제 성공"
                }
        }
    }
    pass