from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas import ContactModel, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=List[ContactResponse], name='Get a list of contacts',
            description='Request limit exceeded', dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def get_contact_by_params(skip: int = 0, limit: int = Query(default=10),
                                first_name: Optional[str] = Query(default=None),
                                last_name: Optional[str] = Query(default=None),
                                email: Optional[str] = Query(default=None),
                                db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact_by_params function is used to get a list of contacts based on the parameters passed in.
        The function will return a list of contacts that match the parameters passed in. If no contact matches, an empty
        array will be returned.

    :param skip: int: Skip the first n number of records
    :param limit: int: Limit the number of contacts returned
    :param first_name: Optional[str]: Filter the contacts by first name
    :param last_name: Optional[str]: Filter the contacts by last name
    :param email: Optional[str]: Filter contacts by email
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A list of contacts that match the parameters
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contacts(skip, limit, first_name, last_name, email, current_user, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")
    return contact


@router.get("/{contact_id}", response_model=ContactResponse, name='Get contact by id',
            description='Request limit exceeded', dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def get_contact(contact_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    It requires an authorization token in order to access it, and will return a 404 error if no contact exists with that ID.

    :param contact_id: int: Get the contact id from the url
    :param db: Session: Get a database session
    :param current_user: User: Get the user that is currently logged in
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, description='Request limit exceeded ',
             dependencies=[Depends(RateLimiter(times=20, seconds=60))], status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactModel object as input, which is validated by pydantic.
        The function also takes an optional db Session object and current_user User object as inputs,
            both of which are provided by dependency injection via FastAPI's Depends decorator.

    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the user id of the logged in user
    :return: A contactmodel object
    :doc-author: Trelent
    """
    new_contact = await repository_contacts.create_contact(body, current_user, db)
    return new_contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes three arguments:
            - body: A ContactModel object containing the new values for the contact.
            - contact_id: An integer representing the ID of an existing contact to be updated.
            - db (optional): A Session object that can be used to access and modify data in a database, if needed.  This is provided by FastAPI's dependency injection system, which we'll learn more about later on in this tutorial series.

    :param body: ContactModel: Get the data from the request body
    :param contact_id: int: Specify the contact that is being updated
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag(contact_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_tag function removes a tag from the database.
        The function takes in an integer contact_id and returns the removed contact.
        If no such contact exists, it raises a 404 error.

    :param contact_id: int: Specify the id of the contact to be removed
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact not found")
    return contact
