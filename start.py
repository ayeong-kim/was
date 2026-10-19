from multiprocessing import Process, Pipe
import uvicorn

from routers.router import app
from process import desk_worker, vet_worker, desk_child, vet_child, desk_channel, vet_channel
from repositorys.repository_manager import init_db
from config import WAS_HOST, WAS_PORT




if __name__ == "__main__":
    init_db()
    Process(target=desk_worker, args=(desk_child,), daemon=True).start()
    Process(target=vet_worker, args=(vet_child,), daemon=True).start()
    desk_child.close()   # 메인은 child 끝을 안 씀 → 워커가 죽으면 요청이 멈추지 않고 에러로 끝남
    vet_child.close()
    desk_channel.start()
    vet_channel.start()

    uvicorn.run(app, host=WAS_HOST, port=WAS_PORT)   # reload 쓰면 Pipe가 워커와 끊김
