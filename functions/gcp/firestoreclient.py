import logging

import firestore as firestore


class FirestoreClient(object):
    _LOG = logging.getLogger(__name__)

    def __init__(self):
        self.client = firestore.Client()

    def is_exits(self, collection, document_id):
        document_ref = self.client.collection(collection).document(document_id)
        document = document_ref.get()
        return document.exists

    def put(self, collection, document_id, document_data):
        self.client.collection(collection).add(document_id=document_id, document_data=document_data)
