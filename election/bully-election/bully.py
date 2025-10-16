import threading
import socket
import time
import json


class Process():
    def __init__(self, process_id, all_process_ids):
        super().__init__()
        self.id = process_id
        self.all_process_ids = all_process_ids  # 全プロセスIDのリスト
        self.leader_id = None  # 現在のリーダーID リーダーが決まったら更新
        self.is_leader = False  # 自分がリーダーかどうか
        self.OK_received = False  # 選挙中にOKメッセージを受信したかどうka
        self.ALIVE_received = False

    def start_election(self):
        message_election = {
                "type": "ELECTION",
                "id": self.id
            }

        for id in range(self.id + 1, max(self.all_process_ids) + 1):
            self.send_message(id, message_election)
        print("\033[36m" + "自分よりIDの大きいプロセスを探す" + "\033[0m")
        time.sleep(1.0)
        if self.OK_received == True:
            self.OK_received = False
            return
        else:
            print("\033[32m" + "自分がリーダーになる" + "\033[0m")
            self.is_leader = True
            self.leader_id = self.id
            message_coordinator = {
                "type": "COORDINATOR",
                "id": self.id
            }
            for id in self.all_process_ids:
                if id != self.id:
                    self.send_message(id, message_coordinator)
        #選挙開始

        

    def keep_listening(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", self.id))
        sock.listen()

        while True:
            client_sock, sender_addr = sock.accept()
            data = client_sock.recv(1024)
            message = json.loads(data.decode("UTF-8"))
            t = threading.Thread(target=self.handle_message, args=(message,))
            t.start()

        #ソケット通信でデータを受信する
        #データを受信したら別スレッドでhandle_messageを呼び出す
    def send_message(self, target_port, message):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        try: 
            sock.connect(("127.0.0.1", target_port))
            json_message = json.dumps(message).encode("UTF-8")
            sock.send(json_message)
        except ConnectionRefusedError:
        #     print(f"[Process {self.id}] Process {target_port} is not available.")
            pass
        finally:
            sock.close()

        #ソケット通信でデータを送信する
        #メッセージにメッセージタイプを付与することで受信側が handle_message() で識別できるようにする

    def handle_message(self, message):   
        message_type = message.get("type")

        if message_type == "ELECTION":
            message_election_ok = {
                "type": "OK"
            }
            message_id = message.get("id")
            self.send_message(message_id, message_election_ok)

        if message_type ==  "OK":
            self.OK_received = True

        if message_type =="COORDINATOR":
            self.is_leader = False
            self.leader_id = message.get("id")

        if message_type =="PING":
            message_id = message.get("id")
            message_PING_ok = {
                "type": "ALIVE"
            }
            self.send_message(message_id, message_PING_ok)

        if message_type =="ALIVE":
            self.ALIVE_received = True





        
        # if message_type == "ELECTION":
        #     message_id = message.get("id")
        #     if message_id < self.id:
        #         self.send_message

            

        #keep_listeningから呼ばれ、受信したメッセージを処理する
        #メッセージタイプに応じて別の処理を行う

    

    def run(self):

        
        # messsage_ok = {
        #     "type": "ELECTION_OK",
        #     "id": sender_id
        # }
        # message_cordinator = {
        #     "type": "CORDINATOR",
        #     "id": new_leader_id
        # }
        # message_ping = {
        #     "type": "PING",
        #     "id": sender_id
        # }
        # message_alive = {
        #     "type": "ALIVE",
        #     "id": sender_id
        # }

    
        print(f"[Process {self.id}] 起動しました。")
        #個別スレッドとしてソケット通信を待つkeep_listeningを起動
        listener_thread = threading.Thread(target=self.keep_listening)
        listener_thread.daemon = True
        listener_thread.start()
        while True:

            if self.is_leader == True:
                print("\033[93m" + "自分がリーダー" + "\033[0m")
                time.sleep(2.0)
                continue

            if self.leader_id == None:
                self.start_election()
                continue
            
            print(f"[Process {self.id}] 現在のリーダー: {self.leader_id}")
            
            message_PING = {
                "type": "PING",
                "id": self.id
            }
            self.send_message(self.leader_id, message_PING)
            time.sleep(2.0)
            
            if self.ALIVE_received == True:
                self.ALIVE_received = False
        
            elif self.ALIVE_received == False:
                print("リーダーがいない、選挙開始")
                self.start_election()


            # 定期的にリーダーの存在を確認し、必要に応じて選挙を開始する
        pass 

if __name__ == "__main__":
    # 簡単なテストのためにプロセスIDをいくつか定義
    process_ids = [10001, 10002, 10003, 10004, 10005]

    # ユーザーにどのプロセスを起動するか選ばせる
    #0なら10001、1なら10002、2なら10003を起動という具合
    index = input("Enter index (0, 1, or 2) to kill corresponding process after start: ")
    index = int(index) if index.isdigit() else None
    p = Process(process_ids[index], process_ids) 
    p.run()