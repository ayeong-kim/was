from routers.datamodels.desk_datamodels import OwnerResponse
from repositorys.repository_manager import transaction
from services.owner_service import OwnerService
from services.pet_service import PetService
from services.consultation_service import ConsultationService
from services.user_service import UserService


class DeskControllers:
    # user: 로그인한 간호사 → user.branch 지점의 데이터만 다룸
    def __init__(self):
        self.owner_service = OwnerService()
        self.pet_service = PetService()
        self.consultation_service = ConsultationService()
        self.user_service = UserService()

    async def regist_owner(self, data, user):
        async with transaction():                 # 주인 + 동물 전부 저장 또는 전부 취소
            oid = await self.owner_service.regist(data, user.branch)
            pets = await self.pet_service.regist(oid, data.pets)
        return OwnerResponse(oid=oid, oname=data.oname, pnum=data.pnum, address=data.address, pets=pets)

    async def get_owner(self, oid, user):
        owner = await self.owner_service.get(oid, user.branch)
        if owner is None:
            return None
        return OwnerResponse(**owner, pets=await self.pet_service.find_by_owner(oid))

    async def search_owner(self, oname, user):
        return [OwnerResponse(**owner, pets=await self.pet_service.find_by_owner(owner["oid"]))
                for owner in await self.owner_service.search(oname, user.branch)]

    async def update_owner(self, oid, data, user):
        if await self.owner_service.get(oid, user.branch) is None:
            return None
        await self.owner_service.update(oid, data)
        return await self.get_owner(oid, user)

    async def get_pet(self, pid, user):
        return await self.pet_service.get(pid, user.branch)

    async def update_pet(self, pid, data, user):
        if await self.pet_service.get(pid, user.branch) is None:
            return None
        await self.pet_service.update(pid, data)
        return await self.pet_service.get(pid, user.branch)

    async def add_pets(self, data, user):
        if await self.owner_service.get(data.oid, user.branch) is None:
            return None
        async with transaction():                 # 동물 여러 마리 전부 저장 또는 전부 취소
            await self.pet_service.regist(data.oid, data.pets)
        return await self.get_owner(data.oid, user)

    async def regist_consultation(self, pid, data, user):
        # 같은 지점 동물 + 같은 지점 수의사에게만 배정
        if await self.pet_service.get(pid, user.branch) is None or all(vet.uid != data.vet_uid for vet in await self.user_service.vets(user.branch)):
            return None
        return await self.consultation_service.regist(pid, data)

    async def get_consultations(self, pid, user):
        return await self.consultation_service.history(pid, user.branch)

    async def get_vets(self, user):
        return await self.user_service.vets(user.branch)
