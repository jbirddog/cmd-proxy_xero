import json

from datetime import datetime, timedelta

from xero_python.accounting import AccountingApi, Contact, LineItem, Invoice, Invoices
from xero_python.api_client import ApiClient, serialize
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.api_client.configuration import Configuration
from xero_python.identity import IdentityApi
from xero_python.api_client.serializer import serialize

class CreateInvoice:
    def __init__(self, 
        client_id: str, 
        client_secret: str, 
        access_token, 

        description: str,
        contact_name: str,
        contact_email: str,
        amount: str,

        #reference: str,
        #created_date: str,
        #due_date: str,
        #account_code: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.description = description
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.amount = amount

    def execute(self):
        """Creates an invoice in xero."""

        access_token = json.loads(self.access_token)

        api_client = ApiClient(
            Configuration(
                debug=True,
                oauth2_token=OAuth2Token(
                    client_id=self.client_id, client_secret=self.client_secret
                ),
            ),
            pool_threads=1,
        )

        @api_client.oauth2_token_getter
        def obtain_xero_oauth2_token():
            return access_token

        @api_client.oauth2_token_saver
        def store_xero_oauth2_token(token):
            access_token = token

        api_instance = AccountingApi(api_client)
        summarize_errors = 'True'
        unitdp = 2
        date_value = datetime.now()
        due_date_value = date_value + timedelta(days=7)

        contact = Contact(name = self.contact_name, 
                email_address = self.contact_email)

        line_item = LineItem(
            description = self.description,
            quantity = 1.0,
            unit_amount = self.amount,
            account_code = "400",
            tracking = [])
    
        line_items = []    
        line_items.append(line_item)

        invoice = Invoice(
            type = "ACCREC",
            contact = contact,
            date = date_value,
            due_date = due_date_value,
            line_items = line_items,
            reference = "Created by SpiffWorkflow",
            status = "AUTHORISED")

        invoices = Invoices(invoices = [invoice])

        try:
            xero_tenant_id = self._get_xero_tenant_id(api_client, access_token)
            created_invoices = api_instance.create_invoices(xero_tenant_id, 
                invoices, summarize_errors, unitdp)
            response = json.dumps(serialize(created_invoices))
            status = 200
        except Exception as e:
            # TODO better error logging/reporting in debug
            response = f'{{ "error": "{e.reason}" }}'
            status = 500

        return {
            'response': response,
            'status': status,
            'mimetype': 'application/json'
        }

    def _get_xero_tenant_id(self, api_client, token):
        if not token:
            return None

        identity_api = IdentityApi(api_client)
        for connection in identity_api.get_connections():
            if connection.tenant_type == "ORGANISATION":
                return connection.tenant_id
