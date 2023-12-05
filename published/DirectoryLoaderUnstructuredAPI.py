"""
Title: Directory Loader using Unstructured API with Error Handling and LangChain Document Output

Description: A class for loading documents from a directory using the LangChain format.
It supports recursive loading and conversion of documents to the LangChain Document class using the UnstructuredClient API.
The class includes built-in error handling and outputs documents in the same style as the LangChain Document class.

To use, get a free unstructured API key here: https://unstructured.io/api-key

Author: @CivilEngineerUK
Date: 02-12-2023
"""

import glob
import os
from typing import List
import asyncio
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError
from langchain.docstore.document import Document

class CustomDirectoryLoaderAPI():
    def __init__(self, api_key: str, path: str, glob: str = "*"):
        """
        Initialize the CustomDirectoryLoaderAPI class.

        Args:
            api_key (str): The API key for the Unstructured API.
            path (str): The path to the directory containing the documents.
            glob (str, optional): The file pattern to match. Defaults to "*".
        """
        self.api_key = api_key
        self.path = path
        self.glob = glob
        self.failed_loads = []

    async def load(self) -> List[Document]:
        """
        Load the documents from the specified directory.

        Returns:
            List[Document]: The loaded documents.
        """
        file_paths = glob.glob(os.path.join(self.path, self.glob), recursive=True)
        print(f"Loading {len(file_paths)} {self.glob} documents from directory: {self.path}")
        converted_documents = await self.convert_documents_to_langchain_format(file_paths)
        print(f"Loaded {len(converted_documents)} documents from directory: {self.path}")
        return converted_documents

    async def convert_documents_to_langchain_format(self, file_paths: List[str], **kwargs) -> List[Document]:
        """
        Convert the documents to the LangChain format.

        Args:
            file_paths (List[str]): The paths of the documents to convert.

        Returns:
            List[Document]: The converted documents.
        """
        unstructured_client = UnstructuredClient(api_key_auth=self.api_key)
        converted_documents = []

        for file_path in file_paths:
            with open(file_path, "rb") as file:
                partition_params = shared.PartitionParameters(
                    files=shared.Files(
                        content=file.read(),
                        file_name=file_path,
                    ),
                    strategy="fast",
                    **kwargs
                )

                try:
                    response = unstructured_client.general.partition(partition_params)
                    converted_document = self.parse_unstructured_response(response)
                    converted_documents.append(converted_document)
                except SDKError as e:
                    self._handle_load_error(file_path, e)

        return converted_documents

    def parse_unstructured_response(self, response) -> Document:
        """
        Parse the response from the Unstructured API and create a LangChain Document.

        Args:
            response: The response from the Unstructured API.

        Returns:
            Document: The parsed LangChain Document.
        """
        elements = response.elements
        page_content = ""
        metadata = {
            "source": elements[0]["metadata"].get("filename", ""),
            "filename": elements[0]["metadata"].get("filename", ""),
            "page_number": elements[0]["metadata"].get("page_number", ""),
        }

        for element in elements:
            if element.get("text"):
                page_content += element["text"] + "\n"

        return Document(page_content=page_content, metadata=metadata)

    def _handle_load_error(self, path, error):
        """
        Handle the error that occurred during document loading.

        Args:
            path (str): The path of the document that failed to load.
            error: The error that occurred.
        """
        self.failed_loads.append((path, str(error)))


async def test_custom_directory_loader_api():
    api_key = "your_api_key"  # get it here https://unstructured.io/api-key
    path = "path/to/directory"
    glob = "*"  # Match all file types

    loader = CustomDirectoryLoaderAPI(api_key, path, glob)
    documents = await loader.load()

    for document in documents:
        print(f"Document: {document.metadata['filename']}")
        print(f"Content:\n{document.page_content}\n")

# Run the test function
asyncio.run(test_custom_directory_loader_api())
