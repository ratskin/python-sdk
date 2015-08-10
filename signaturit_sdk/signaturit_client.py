from resources.connection import Connection
from resources.parser import Parser


class SignaturitClient:
    ACCOUNT_URL = '/v2/account.json'
    ACCOUNT_STORAGE_URL = '/v2/account/storage.json'

    BRANDINGS_URL = '/v2/brandings.json'
    BRANDINGS_ID_URL = '/v2/brandings/%s.json'
    BRANDINGS_LOGO_URL = '/v2/brandings/%s/%s.json'
    BRANDINGS_TEMPLATES_URL = '/v2/brandings/%s/%s/%s.json'

    EMAILS_URL = '/v3/emails.json'
    EMAILS_COUNT_URL = '/v3/emails/count.json'
    EMAILS_ID_URL = '/v3/emails/%s.json'
    EMAILS_CERTIFICATES_URL = '/v3/emails/%s/certificates.json'
    EMAILS_CERTIFICATES_ID_URL = '/v3/emails/%s/certificates/%s.json'
    EMAILS_AUDIT_TRAIL = '/v3/emails/%s/certificates/%s/download/audit_trail'
    EMAILS_ORIGINAL = '/v3/emails/%s/certificates/%s/download/original'

    CREATE_EMAIL_PARAMS = ['send_email_event', 'files', 'recipients', 'subject', 'body']

    CREATE_SIGN_PARAMS = ['subject', 'body', 'recipients', 'files', 'in_person_sign', 'sequential', 'mandatory_pages',
                          'mandatory_photo', 'mandatory_voice', 'branding_id', 'templates', 'method', 'sms_auth',
                          'data', 'signature_pos_x', 'signature_pos_y']

    STORAGE_S3 = ['bucket', 'key', 'secret']

    STORAGE_SFTP_PASSWORD = ['password']
    STORAGE_SFTP_KEY = ['passphrase', 'public', 'private']
    STORAGE_SFTP = ['auth_method', 'host', 'port', 'dir', 'user']

    DOCUMENT_STORAGE = ['type']
    DOCUMENT_STORAGE_ALL = DOCUMENT_STORAGE + STORAGE_SFTP + STORAGE_SFTP_KEY + STORAGE_SFTP_PASSWORD + STORAGE_S3

    PRODUCTION = True

    SIGNS_URL = '/v2/signs.json'
    SIGNS_CANCEL_URL = '/v2/signs/%s/cancel.json'
    SIGNS_COUNT_URL = '/v2/signs/count.json'
    SIGNS_ID_URL = '/v2/signs/%s.json'
    SIGNS_DOCUMENTS_URL = '/v2/signs/%s/documents.json'
    SIGNS_DOCUMENTS_ID_URL = '/v2/signs/%s/documents/%s.json'
    SIGNS_DOCUMENTS_AUDIT_URL = '/v2/signs/%s/documents/%s/download/doc_proof'
    SIGNS_DOCUMENTS_SIGNED_URL = '/v2/signs/%s/documents/%s/download/signed'
    SIGNS_SEND_REMINDER_URL = '/v2/signs/%s/documents/%s/reminder.json'

    TEMPLATES_URL = '/v2/templates.json'

    TOUCH_BRANDING_PARAMS = ['files', 'primary', 'events_url', 'subject_tag', 'corporate_layout_color',
                             'corporate_text_color',
                             'application_texts', 'reminders', 'expire_time', 'callback_url', 'signature_pos_x',
                             'signature_pos_y', 'terms_and_conditions_label', 'terms_and_conditions_text']

    def __init__(self, token, production=False):
        self.token = token
        self.production = production

    def get_account(self):
        """
        Get info from your account
        @return Account data
        """
        connection = Connection(self.token)
        connection.set_url(self.production, self.ACCOUNT_URL)

        return connection.get_request()

    def get_signature(self, signature_id):
        """
        Get a concrete Signature
        @return Signature data
        """
        connection = Connection(self.token)
        connection.set_url(self.production, self.SIGNS_ID_URL % signature_id)

        return connection.get_request()

    def get_signatures(self, limit=100, offset=0, conditions={}):
        """
        Get all signatures
        """
        url = self.SIGNS_URL + "?limit=%s&offset=%s" % (limit, offset)

        for key, value in conditions.items():
            if key is 'ids':
                ids = ",".join(value)
                url += '&ids=%s' % ids
                continue

            if key is 'data':
                for data_key, data_value in value.items():
                    url += '&data.%s=%s' % (data_key, data_value)

                continue

            url += '&%s=%s' % (key, value)

        connection = Connection(self.token)
        connection.set_url(self.production, url)

        return connection.get_request()

    def count_signatures(self, conditions={}):
        """
        Count all signatures
        """
        url = self.SIGNS_COUNT_URL + '?'

        for key, value in conditions.items():
            if key is 'ids':
                ids = ",".join(value)
                url += '&ids=%s' % ids
                continue

            if key is 'data':
                for data_key, data_value in value.items():
                    url += '&data.%s=%s' % (data_key, data_value)

                continue

            url += '&%s=%s' % (key, value)

        connection = Connection(self.token)
        connection.set_url(self.production, url)

        return connection.get_request()

    def get_signature_document(self, signature_id, document_id):
        """
        Get a concrete document from a concrete Signature
        @return Document data
        """
        connection = Connection(self.token)
        connection.set_url(self.production, self.SIGNS_DOCUMENTS_ID_URL % (signature_id, document_id))

        return connection.get_request()

    def get_signature_documents(self, signature_id):
        """
        Get all documents from a concrete Signature
        @return List of documents
        """
        connection = Connection(self.token)
        connection.set_url(self.production, self.SIGNS_DOCUMENTS_URL % signature_id)

        return connection.get_request()

    def download_audit_trail(self, signature_id, document_id, path):
        """
        Get the audit trail of concrete document
        @signature_id: Id of signature
        @document_id: Id of document
        @path: Path where the document will be stored
        """
        connection = Connection(self.token)
        connection.set_url(self.production, self.SIGNS_DOCUMENTS_AUDIT_URL % (signature_id, document_id))

        response, headers = connection.file_request()

        if headers['content-type'] == 'application/json':
            return response

        f = open(path, 'w')
        f.write(response)
        f.close()

    def download_signed_document(self, signature_id, document_id, path):
        """
        Get the audit trail of concrete document
        @signature_id: Id of signature
        @document_id: Id of document
        @path: Path where the document will be stored
        """
        connection = Connection(self.token)

        connection.set_url(self.production, self.SIGNS_DOCUMENTS_SIGNED_URL % (signature_id, document_id))

        response, headers = connection.file_request()

        if headers['content-type'] == 'application/json':
            return response

        f = open(path, 'w')
        f.write(response)
        f.close()

    def create_signature(self, files, recipients, params):
        """
        Create a new Signature request.
        @files
            Files to send
                ex: ['/documents/internet_contract.pdf', ... ]
        @recipients
            A dictionary with the email and fullname of the person you want to sign.
            If you wanna send only to one person:
               - [{"email": "john_doe@gmail.com", "fullname": "John"}]
            For multiple recipients, yo need to submit a list of dicts:
               - [{"email": "john_doe@gmail.com", "fullname": "John"}, {"email":"bob@gmail.com", "fullname": "Bob"}]
            You can attach a phone number to each recipient, and then, the user will receive a security code in his smartphone.
               - [{"email": "john_doe@gmail.com", "fullname": "John", "phone": "XXXX"}]
        @params: An array of params
            - subject: Subject of the email (optional)
            - body: Body of the email (optional)
            - in_person_sign: If you want to do an in person sign (system will not send an email to the user, but return the
                         sign url instead) (optional)
            - sequential: If you want to do a sequential sign (for multiple recipients, the sign goes in sequential way)
                          (optional)
            - mandatory_photo: A list of booleans that tell if photo capture will be asked to finish the signature process. (optional)
            The index of array references the document number, so first value will apply to first document.
            - mandatory_voice: A list of booleans that tell if audio recording will be asked to finish the signature process. (optional)
            The index of array references the document number, so first value will apply to first document.
            - mandatory_pages: A list of list of pages the signer must sign (optional)
            The index of array references the document number, so first value will apply to first document.
                ex: [[1, 2, 5], [1]]
            - branding_id: The id of the branding you want to use. If no branding_id, system use the account default
                           branding. (optional)
        """
        params['files'] = files
        params['recipients'] = recipients

        parser = Parser(self.CREATE_SIGN_PARAMS, [])
        params, files = parser.parse_data(params)

        connection = Connection(self.token)
        connection.set_url(self.production, self.SIGNS_URL)
        connection.add_params(params)
        connection.add_files(files)

        return connection.post_request()

    def cancel_signature(self, signature_id):
        """
        Cancel a concrete Signature
        @signature_id: Id of signature
        @return Signature data
        """
        connection = Connection(self.token)

        connection.set_url(self.production, self.SIGNS_CANCEL_URL % signature_id)

        return connection.patch_request()

    def send_signature_reminder(self, signature_id, document_id):
        """
        Send a reminder email
        @signature_id: Id of signature
        @document_id: Id of document
        """
        connection = Connection(self.token)

        connection.set_url(self.production, self.SIGNS_SEND_REMINDER_URL % (signature_id, document_id))

        return connection.post_request()

    def get_branding(self, branding_id):
        """
        Get a concrete branding
        @branding_id: Id of the branding to fetch
        @return Branding
        """
        connection = Connection(self.token)

        connection.set_url(self.production, self.BRANDINGS_ID_URL % branding_id)

        return connection.get_request()

    def get_brandings(self):
        """
        Get all account brandings
        @return List of brandings
        """
        connection = Connection(self.token)

        connection.set_url(self.production, self.BRANDINGS_URL)

        return connection.get_request()

    def create_branding(self, params):
        """
        Create a new branding
        @params: An array of params (all params are optional)
            - primary: If set, this new branding will be the default one.
            - corporate_layout_color: Default color for all application widgets (hex code)
            - corporate_text_color: Default text color for all application widgets (hex code)
            - application_texts: A dict with the new text values
                - sign_button: Text for sign button
                - send_button: Text for send button
                - decline_button: Text for decline button:
                - decline_modal_title: Title for decline modal (when you click decline button)
                - decline_modal_body: Body for decline modal (when you click decline button)
                - photo: Photo message text, which tells the user that a photo is needed in the current process
                - multi_pages: Header of the document, which tells the user the number of pages to sign
                ex: { 'photo': 'Hey! Take a photo of yourself to validate the process!'}
            - subject_tag: This tag appears at the subject of all your messages
                ex: [ your_tag ] Pending document
            - reminders: A list with reminder times (in seconds). Every reminder time, a email will be sent, if the
                        signer didn't sign the document
                ex: [ 3600 ] (At 30 minutes of sending the email))
            - expire_time: The signature time (in seconds). When the expire time is over, the document cannot be signed.
                           Set 0 if you want a signature without expire time.
            - callback_url: A url to redirect the user, when the process is over.
            - events_url: A url to send system event notifications
            - signature_pos_x: Default position x of signature
            - signature_pos_y: Default position y of signature
            - terms_and_conditions_label: The terms text that appears when you need to check the button to accept.
            - terms_and_conditions_body: Custom text that appears below signature conditions

        @return: A dict with branding data
        """
        parser = Parser(self.TOUCH_BRANDING_PARAMS, [])
        parser.validate_data(params)

        connection = Connection(self.token)

        connection.add_header('Content-Type', 'application/json')
        connection.set_url(self.production, self.BRANDINGS_URL)
        connection.add_params(params, json_format=True)

        return connection.post_request()

    def update_branding(self, branding_id, params):
        """
        Update a existing branding
        @branding_id: Id of the branding to update
        @params: Same params as method create_branding, see above
        @return: A dict with updated branding data
        """
        parser = Parser(self.TOUCH_BRANDING_PARAMS, [])
        parser.validate_data(params)

        connection = Connection(self.token)

        connection.add_header('Content-Type', 'application/json')
        connection.set_url(self.production, self.BRANDINGS_ID_URL % branding_id)
        connection.add_params(params)

        return connection.patch_request()

    def update_branding_logo(self, branding_id, file_path):
        """
        Update the logo of a branding
        """
        params = {'files': file_path}

        parser = Parser(self.TOUCH_BRANDING_PARAMS, [])
        params, files = parser.parse_data(params)

        connection = Connection(self.token)

        connection.add_files(files)
        connection.set_url(self.production, self.BRANDINGS_LOGO_URL % (branding_id, 'logo'))

        return connection.put_request()

    def update_branding_email(self, branding_id, template, file_path):
        """
        Update the template of a branding
        """
        params = {'files': file_path}

        parser = Parser(self.TOUCH_BRANDING_PARAMS, [])
        params, files = parser.parse_data(params)

        connection = Connection(self.token)

        connection.add_files(files)
        connection.set_url(self.production, self.BRANDINGS_TEMPLATES_URL % (branding_id, 'emails', template))

        return connection.put_request()

    def get_templates(self, limit=100, offset=0):
        """
        Get all account templates
        """
        url = self.TEMPLATES_URL + "?limit=%s&offset=%s" % (limit, offset)

        connection = Connection(self.token)

        connection.set_url(self.production, url)

        return connection.get_request()

    def get_emails(self, limit=100, offset=0, conditions={}):
        """
        Get all certified emails
        """
        url = self.EMAILS_URL + "?limit=%s&offset=%s" % (limit, offset)

        connection = Connection(self.token)

        for key, value in conditions.items():
            url += "&%s=%s" % (key, value)

        connection.set_url(self.production, url)

        return connection.get_request()

    def count_emails(self, conditions={}):
        """
        Count all certified emails
        """
        url = self.EMAILS_COUNT_URL + "?"

        connection = Connection(self.token)

        for key, value in conditions.items():
            url += "&%s=%s" % (key, value)

        connection.set_url(self.production, url)

        return connection.get_request()

    def get_email(self, email_id):
        """
        Get a specific email
        """
        connection = Connection(self.token)

        connection.set_url(self.production, self.EMAILS_ID_URL % email_id)

        return connection.get_request()

    def get_email_certificates(self, email_id):
        """
        Get certificates from a specific email
        """
        connection = Connection(self.token)

        connection.set_url(self.production, self.EMAILS_CERTIFICATES_URL % email_id)

        return connection.get_request()

    def get_email_certificate(self, email_id, certificate_id):
        """
        Get single certificate from a specific email
        """
        connection = Connection(self.token)

        connection.set_url(self.production, self.EMAILS_CERTIFICATES_ID_URL % (email_id, certificate_id))

        return connection.get_request()

    def download_email_audit_trail(self, email_id, certificate_id, path):
        connection = Connection(self.token)

        connection.set_url(self.production, self.EMAILS_AUDIT_TRAIL % (email_id, certificate_id))

        response, headers = connection.file_request()

        if headers['content-type'] == 'application/json':
            return response

        f = open(path, 'w')
        f.write(response)
        f.close()

    def download_email_original_file(self, email_id, certificate_id, path):
        connection = Connection(self.token)

        connection.set_url(self.production, self.EMAILS_ORIGINAL % (email_id, certificate_id))

        response, headers = connection.file_request()

        if headers['content-type'] == 'application/json':
            return response

        f = open(path, 'w')
        f.write(response)
        f.close()

    def create_email(self, files, recipients, subject, body, params):
        """
        Create a new certified email

        @files
             Files to send
                ex: ['/documents/internet_contract.pdf', ... ]
        @recipients
            A dictionary with the email and fullname of the person you want to sign.
            If you wanna send only to one person:
               - [{"email": "john_doe@gmail.com", "fullname": "John"}]
            For multiple recipients, yo need to submit a list of dicts:
               - [{"email": "john_doe@gmail.com", "fullname": "John"}, {"email":"bob@gmail.com", "fullname": "Bob"}]
        @subject
            Email subject
        @body
            Email body
        @params
            Optional parameters
            send_email_event: Chooses the event that will trigger the audit trail generation
                - delivered: When email is delivered
                - seen: When app is opened (only emails with pdfs attached)
                - opened: When document is opened (only emails with pdfs attached)
        """
        params['files'] = files
        params['recipients'] = recipients
        params['subject'] = subject
        params['body'] = body

        parser = Parser(self.CREATE_EMAIL_PARAMS, [])
        params, files = parser.parse_data(params)

        connection = Connection(self.token)
        connection.set_url(self.production, self.EMAILS_URL)
        connection.add_params(params)
        connection.add_files(files)

        return connection.post_request()