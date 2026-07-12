import os
from django.conf import settings
from rest_framework.exceptions import ParseError
from rest_framework_xml.parsers import XMLParser
from lxml import etree
import xmlschema

class AssetFlowXMLParser(XMLParser):
    """
    Custom XML Parser that:
    1. Is XXE-safe (resolve_entities=False, no_network=True, load_dtd=False) via lxml
    2. Validates incoming XML against XSD schemas in /schemas before business logic
    """
    media_type = 'application/xml'

    def parse(self, stream, media_type=None, parser_context=None):
        # 1. Parse safely with lxml
        parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
        try:
            tree = etree.parse(stream, parser)
        except etree.XMLSyntaxError as exc:
            raise ParseError(f'XML parse error - {exc}')

        root = tree.getroot()
        root_tag = root.tag

        # 2. Validate against XSD
        schema_path = os.path.join(settings.BASE_DIR, 'schemas', f'{root_tag}.xsd')
        if os.path.exists(schema_path):
            try:
                schema = xmlschema.XMLSchema(schema_path)
                schema.validate(tree)
            except xmlschema.XMLSchemaValidationError as exc:
                raise ParseError(f'XML schema validation error - {exc}')
        
        # 3. Reset stream and use DRF XML base parser to convert safely into dict
        stream.seek(0)
        return super().parse(stream, media_type, parser_context)
