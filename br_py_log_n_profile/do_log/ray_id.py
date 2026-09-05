import uuid
from contextvars import ContextVar

ray_id_var: ContextVar[uuid.UUID | None] = ContextVar("ray_id")


def set_ray_id(id: uuid.UUID) -> None:
    ray_id_var.set(id)


def get_ray_id(generate: bool = True) -> uuid.UUID | None:
    id_of_ray = ray_id_var.get(None)
    if generate and id_of_ray is None:
        id_of_ray = ray_id(source_type=0)
        set_ray_id(id_of_ray)
    return id_of_ray


def ray_id(source_type: int, id_of_ray: uuid.UUID | None = None) -> uuid.UUID:
    if id_of_ray is not None:
        return id_of_ray
    id_of_ray = uuid.uuid1(node=source_type)
    return id_of_ray
