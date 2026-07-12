from rest_framework_xml.renderers import XMLRenderer
from django.utils.encoding import force_str

class AssetFlowXMLRenderer(XMLRenderer):
    """
    Custom XML Renderer that enforces the <response> root tag.
    The response data should already be structured with <data>, <meta>, or <error> keys
    either by the view or the exception handler.
    """
    root_tag_name = 'response'

    def _to_xml(self, xml, data, parent_tag=None):
        if isinstance(data, (list, tuple)):
            item_tag = self.item_tag_name
            if parent_tag == 'custom_fields':
                item_tag = 'field'
            elif parent_tag == 'departments':
                item_tag = 'department'
            elif parent_tag == 'categories':
                item_tag = 'category'
            elif parent_tag == 'employees':
                item_tag = 'employee'
            elif parent_tag and parent_tag.endswith('s'):
                item_tag = parent_tag[:-1]
                
            for item in data:
                if item_tag == 'field' and isinstance(item, dict):
                    # We render it as a tag with attributes
                    attrs = {}
                    for k, v in item.items():
                        if isinstance(v, bool):
                            attrs[k] = 'true' if v else 'false'
                        elif v is not None:
                            attrs[k] = str(v)
                    xml.startElement(item_tag, attrs)
                    xml.endElement(item_tag)
                else:
                    xml.startElement(item_tag, {})
                    self._to_xml(xml, item, parent_tag=item_tag)
                    xml.endElement(item_tag)

        elif isinstance(data, dict):
            for key, value in data.items():
                xml.startElement(key, {})
                self._to_xml(xml, value, parent_tag=key)
                xml.endElement(key)

        elif data is None:
            pass

        else:
            xml.characters(force_str(data))
