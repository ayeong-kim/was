from repositorys.owner_repository import OwnerRepository


class OwnerService:
    def __init__(self):
        self.owner_repository = OwnerRepository()

    async def regist(self, data, branch):
        return await self.owner_repository.insert(data, branch)

    async def get(self, oid, branch):
        return await self.owner_repository.find(oid, branch)

    async def search(self, oname, branch):
        return await self.owner_repository.find_by_name(oname, branch)

    async def update(self, oid, data):
        fields = data.model_dump(exclude_unset=True)
        if fields:
            await self.owner_repository.update(oid, fields)
