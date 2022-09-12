import json

def create_invoice(
        client_id: str, 
        #client_secret: str, 
        #access_token: str, 
        #tenant_id: str,
        #due_date: str
    ):
    """Creates an invoice in xero."""
    return {
        'response': json.dumps({'todo': f'create invoice in xero with client_id: {client_id}' }),
        'status': 200,
        'mimetype': 'application/json'
    }
