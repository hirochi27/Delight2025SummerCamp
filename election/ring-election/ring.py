import threading
import time
import socket
import json
#gitの確認

class Process():
    def __init__(self, process_id, all_process_ids):
        super().__init__()
        self.id = process_id
        #self.ids = ids
        self.all_process_ids = all_process_ids  # 全プロセスIDのリスト
        self.leader_id = None  # 現在のリーダーID リーダーが決まったら更新
        self.send_OK = False
        self.is_leader = False
        self.ALIVE_received = False
        #self.OK_received = False #メッセージをうけとったか


    def start_election(self):
        message_election = {
            "type": "ELECTION",
            "ids": [self.id]
            #↑自分のIDを追加した配列
        }
    
        current_index = self.all_process_ids.index(self.id)
        next_index = (current_index + 1) % len(self.all_process_ids)
        next_id = self.all_process_ids[next_index]

        if self.send_OK == True:
            self.send_OK = False
            
        
        # if self.id in self.ids and len(self.ids) >= 2:
        #     pass
        # else:
        self.send_message(next_id, message_election)
        time.sleep(1.0)

    def start_coordinator(self):
        message_coordinator = {
            "type": "COORDINATOR",
            "leader_id": self.leader_id,
            "sender_id": self.id
        }

        current_index = self.all_process_ids.index(self.id)
        next_index = (current_index + 1) % len(self.all_process_ids)
        next_id = self.all_process_ids[next_index]

        self.send_message(next_id, message_coordinator)
        time.sleep(1.0)



    def keep_listening(self):
        #ソケット通信でデータを受信する
        #データを受信したら別スレッドでhandle_messageを呼び出す
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", self.id))
        sock.listen()

        while True:
            client_sock, sender_adde = sock.accept()
            data = client_sock.recv(1024)
            message = json.loads(data.decode("UTF-8"))
            t = threading.Thread(target=self.handle_message, args = (message,))
            t.start()

    def send_message(self, target_port, message):
        #ソケット通信でデータを送信する
        #メッセージにメッセージタイプを付与することで受信側が handle_message() で識別できるようにする
        
        counter = 0
        while counter < len(self.all_process_ids):  
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
            current_index = self.all_process_ids.index(self.id)
            next_index = (current_index + 1 + counter) % len(self.all_process_ids)
            target_port = self.all_process_ids[next_index]
            try:
                sock.connect(("127.0.0.1", target_port))
                json_message = json.dumps(message).encode("UTF-8")
                sock.send(json_message)    
                self.send_OK = True  
                print("can send election to" + str(target_port))            
            except ConnectionRefusedError:
                counter += 1 
                sock.close() 
                next_index + 1    
                print(target_port) 
            finally:           
                if self.send_OK == True:
                    sock.close()
                    break#while文終わらせる
                    


    def handle_message(self, message):
        #keep_listeningから呼ばれ、受信したメッセージを処理する
        #メッセージタイプに応じて別の処理を行う
        message_type = message.get("type")
        message_ids = message.get("ids")

        if message_type == "ELECTION":
            print("OK" + str(message_ids))
            if self.id in message_ids:
                ##配列の中の最大値をリーダーに
                #if self.leader_id == max(message_ids): 
                    #self.leader_id = 
                    #if self.leader_id <= max(message_ids):
                        #self.leader_id
                self.leader_id = max(message_ids)
                self.start_coordinator()
                #self.start_leader_message()
                print(str(self.leader_id) + "がリーダー")
                time.sleep(2.0)
            else:    
                message_ids.append(self.id)
                message_election = {
                    "type": "ELECTION",
                    "ids": message_ids
                }       
                current_index = self.all_process_ids.index(self.id)
                next_index = (current_index + 1) % len(self.all_process_ids)
                next_id = self.all_process_ids[next_index]
                self.send_message(next_id, message_election)

        if message_type == "COORDINATOR":
            message_leader_id = message.get("leader_id")
            message_sender_id = message.get("sender_id")
            print("coordinator受信{message_leader_id}" )
            self.leader_id = message_leader_id 
            if self.id == message_sender_id:
                print("COORDINATORメッセージが一周しました")
                return
            elif self.leader_id == self.id:
                self.is_leader = True
                message_coordinator = {
                    "type": "COORDINATOR",
                    "leader_id": message_leader_id,
                    "sender_id": message_sender_id
                    }
                current_index =self.all_process_ids.index(self.id)
                next_index = (current_index + 1) %len(self.all_process_ids)
                next_id =self.all_process_ids[next_index]
                self.send_message(next_id,message_coordinator)
            else:
                current_index =self.all_process_ids.index(self.id)
                next_index = (current_index + 1) %len(self.all_process_ids)
                next_id =self.all_process_ids[next_index]
                self.send_message(next_id,message_coordinator)

        if message_type == "PING":
            message_id = message.get("id")
            message_PING_ok = {
                "type" : "ALIVE"
            }
            self.send_message(message_id, message_PING_ok)

        if message_type == "ALIVE":
            self.ALIVE_received = True


    def run(self):
        print(f"[Process {self.id}] 起動しました。")
        #個別スレッドとしてソケット通信を待つkeep_listeningを起動
        listener_thread = threading.Thread(target=self.keep_listening)
        listener_thread.daemon = True
        listener_thread.start()

        while True:
            if self.leader_id == None:
                self.start_election()
                continue
            print("現在のリーダー" + str(self.leader_id))
            time.sleep(2.0)
            # 定期的にリーダーの存在を確認し、必要に応じて選挙を開始する
            
            message_PING = {
                "type": "PING",
                "id": self.id
            }
            self.send_message(self.leader_id, message_PING)
            time.sleep(2.0)

            
            if self.ALIVE_received == False:
                print("リーダーがいない、選挙開始")
                self.start_election()
            
            elif self.ALIVE_received == True:
                self.ALIVE_received = False
        

            # if self.ALIVE_received == False:
            #     print("リーダーがいない、選挙開始") 
            #     self.start_election()
            # else:
            #     self.ALIVE_received = False
                


if __name__ == "__main__":
    # 簡単なテストのためにプロセスIDをいくつか定義
    process_ids = [10001, 10002, 10003, 10004, 10005, 10006]

    # ユーザーにどのプロセスを起動するか選ばせる
    #0なら10001、1なら10002、2なら10003を起動という具合
    index = input("Enter index (0, 1, or 2) to kill corresponding process after start: ")
    index = int(index) if index.isdigit() else None
    p = Process(process_ids[index], process_ids) 
    p.run()