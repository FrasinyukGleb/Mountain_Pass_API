import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import List

from test_parameters import *
from src.services.mountain_pass import Mountain_Pass

pytestmark = pytest.mark.asyncio

db = Mountain_Pass()


@pytest.mark.parametrize(
    argnames=('pass_request',),
    argvalues=[
        (ADD_PASS_WITHOUT_IMAGES,),
        (ADD_PASS_OTHER_USER,),
        (ADD_PASS_WITH_IMAGES,),
    ],
    ids=(
            'add_pass_without_images',
            'add_pass_same_user',
            'add_pass_with_images',
    ),
)
async def test_add_mountain_pass(dbsession: AsyncSession, pass_request: PassAddSchema):
    mountain_pass_id = await db.add_mountain_pass(mountain_pass=pass_request, session=dbsession)
    mountain_pass = await db.get_mountain_pass_by_id(mountain_pass_id, dbsession)
    assert mountain_pass is not None
    await db._delete_mountain_pass(mountain_pass=mountain_pass, session=dbsession)


@pytest.mark.parametrize(
    argnames=('pass_request', 'data_to_update'),
    argvalues=[
        (ADD_PASS_WITHOUT_IMAGES, UPDATE_PASS_WITHOUT_IMAGES),
        (ADD_PASS_WITH_IMAGES, UPDATE_PASS_WITH_IMAGES),
        (ADD_PASS_WITHOUT_IMAGES, UPDATE_PASS_WITH_IMAGES),
        (ADD_PASS_WITH_IMAGES, UPDATE_PASS_WITHOUT_IMAGES),
    ],
    ids=(
            'update_pass_without_images',
            'update_pass_other_images',
            'update_pass_add_images',
            'update_pass_delete_images',
    ),
)
async def test_update_mountain_pass(
        dbsession: AsyncSession,
        pass_request: PassAddSchema,
        data_to_update: PassUpdateSchema,
):
    mountain_pass_id = await db.add_mountain_pass(mountain_pass=pass_request, session=dbsession)
    db_mountain_pass = await db.get_mountain_pass_by_id(mountain_pass_id, dbsession)
    await db.update_mountain_pass(db_mountain_pass, data_to_update, dbsession)
    new_mountain_pass = await db.get_mountain_pass_by_id(mountain_pass_id, dbsession)
    new_images = await db._get_images_by_mountain_pass_id(new_mountain_pass.id, dbsession)

    assert data_to_update.title == new_mountain_pass.title
    if data_to_update.images:
        assert len(data_to_update.images) == len(new_images)
    else:
        assert len(new_images) == 0
    await db._delete_mountain_pass(mountain_pass=db_mountain_pass, session=dbsession)


@pytest.mark.parametrize(
    argnames=('pass_request',),
    argvalues=[
        (ADD_PASS_WITHOUT_IMAGES,),
        (ADD_PASS_WITH_IMAGES,),
        (ADD_PASS_OTHER_USER,),
    ],
    ids=(
            'get_info_pass_without_images',
            'get_info_pass_with_images',
            'get_info_pass_other_user',
    ),
)
async def test_get_info_mountain_pass(dbsession: AsyncSession, pass_request: PassAddSchema):
    mountain_pass_id = await db.add_mountain_pass(mountain_pass=pass_request, session=dbsession)
    mountain_pass = await db.get_mountain_pass_by_id(mountain_pass_id, dbsession)
    info_mountain_pass = await db.get_info_mountain_pass(mountain_pass, dbsession)
    assert pass_request.title == info_mountain_pass.title
    assert pass_request.user.email == info_mountain_pass.user.email
    assert pass_request.coords.height == info_mountain_pass.coords.height
    assert pass_request.level.summer == info_mountain_pass.level.summer
    assert len(pass_request.images) == len(info_mountain_pass.images)
    if pass_request.images:
        add_data_title_images = ''.join([image.title for image in pass_request.images])
        info_mountain_pass_title_images = ''.join([image.title for image in info_mountain_pass.images])
        assert add_data_title_images == info_mountain_pass_title_images
    await db._delete_mountain_pass(mountain_pass=mountain_pass, session=dbsession)


@pytest.mark.parametrize(
    argnames=('input_data_mountain_passes', 'user_object', 'col_user_mountain_passes'),
    argvalues=[
        ([ADD_PASS_WITHOUT_IMAGES, ADD_PASS_OTHER_USER], OTHER_USER, 1),
        ([ADD_PASS_WITH_IMAGES, ADD_PASS_WITH_IMAGES], USER_CAT, 0),
        ([ADD_PASS_OTHER_USER, ADD_PASS_OTHER_USER], OTHER_USER, 3),
        ([ADD_PASS_CAT_USER], USER_CAT, 1),
    ],
    ids=(
            'get_user_passes_other_user_one_found',
            'get_user_passes_cat_user_not_found',
            'get_user_passes_other_user_all_found',
            'get_user_passes_cat_user_one_found',
    ),
)
async def test_get_mountain_passes_by_user_id(
        dbsession: AsyncSession,
        input_data_mountain_passes: List,
        user_object: UserSchema,
        col_user_mountain_passes: int,
):
    await db._add_user(user=user_object, session=dbsession)
    for mountain_pass in input_data_mountain_passes:
        await db.add_mountain_pass(mountain_pass=mountain_pass, session=dbsession)
    user = await db.get_user_by_email(user_object.email, dbsession)
    user_mountain_passes = await db.get_mountain_passes_by_user_id(user.id, dbsession)
    assert len(user_mountain_passes) == col_user_mountain_passes
