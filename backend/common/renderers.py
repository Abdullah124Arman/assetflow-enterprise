from rest_framework_xml.renderers import XMLRenderer
from django.utils.encoding import force_str

class AssetFlowXMLRenderer(XMLRenderer):
    """
    Custom XML Renderer that enforces the <response> root tag.
    The response data should already be structured with <data>, <meta>, or <error> keys
    either by the view or the exception handler.
    """
    root_tag_name = 'response'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        rendered = super().render(data, accepted_media_type, renderer_context)
        if not rendered:
            return rendered

        if renderer_context and 'view' in renderer_context:
            view = renderer_context['view']
            schema_name = getattr(view, 'schema_name', None)
            if schema_name:
                from django.conf import settings
                import os
                import xmlschema
                from rest_framework.exceptions import ValidationError
                from lxml import etree
                
                schema_path = os.path.join(settings.BASE_DIR, 'schemas', f'{schema_name}.xsd')
                if os.path.exists(schema_path):
                    try:
                        parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
                        xml_bytes = rendered if isinstance(rendered, bytes) else rendered.encode('utf-8')
                        tree = etree.fromstring(xml_bytes, parser)
                        schema = xmlschema.XMLSchema(schema_path)
                        schema.validate(tree)
                    except Exception as exc:
                        raise ValidationError(f"Response XML does not validate against schema {schema_name}.xsd: {exc}")
        return rendered


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
