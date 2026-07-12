from rest_framework_xml.renderers import XMLRenderer

class AssetFlowXMLRenderer(XMLRenderer):
    """
    Custom XML Renderer that enforces the <response> root tag.
    The response data should already be structured with <data>, <meta>, or <error> keys
    either by the view or the exception handler.
    """
    root_tag_name = 'response'
