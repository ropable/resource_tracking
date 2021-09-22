from tastypie.api import Api
from tracking.api import DeviceResource, LoggedPointResource


v1_api = Api(api_name='v1')
v1_api.register(DeviceResource())
v1_api.register(LoggedPointResource())
