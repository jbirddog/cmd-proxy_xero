import json

from datetime import datetime, timedelta

from xero_python.accounting import AccountingApi, Contact, LineItem, Invoice, Invoices
from xero_python.api_client import ApiClient, serialize
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.api_client.configuration import Configuration
from xero_python.identity import IdentityApi
from xero_python.api_client.serializer import serialize

def create_invoice(
        client_id: str, 
        client_secret: str, 
        access_token, 

        #reference: str,
        description: str,
        contact_id: str,
        #created_date: str,
        #due_date: str,

        amount: str,
        #account_code: str,
    ):
    """Creates an invoice in xero."""

    access_token = json.loads(access_token)

    api_client = ApiClient(
        Configuration(
            debug=True,
            oauth2_token=OAuth2Token(
                client_id=client_id, client_secret=client_secret
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
    xero_tenant_id = get_xero_tenant_id(api_client, access_token)
    summarize_errors = 'True'
    unitdp = 2
    date_value = datetime.now()
    due_date_value = date_value + timedelta(days=7)

    contact = Contact(contact_id = contact_id)

    line_item = LineItem(
        description = description,
        quantity = 1.0,
        unit_amount = amount,
        account_code = "400",
        tracking = []) #line_item_trackings)
    
    line_items = []    
    line_items.append(line_item)

    invoice = Invoice(
        type = "ACCREC",
        contact = contact,
        date = date_value,
        due_date = due_date_value,
        line_items = line_items,
        reference = "Created via Cmd-Proxy",
        status = "AUTHORISED")

    invoices = Invoices( 
        invoices = [invoice])

    created_invoices = api_instance.create_invoices(xero_tenant_id, invoices, summarize_errors, unitdp)
    response = json.dumps(serialize(created_invoices))

    return {
        'response': response, #json.dumps({'todo': f'create invoice in xero {access_token}' }),
        'status': 200,
        'mimetype': 'application/json'
    }

def get_xero_tenant_id(api_client, token):
    if not token:
        return None

    identity_api = IdentityApi(api_client)
    for connection in identity_api.get_connections():
        if connection.tenant_type == "ORGANISATION":
            return connection.tenant_id
