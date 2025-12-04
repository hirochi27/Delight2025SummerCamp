import threading

class Process():
    def __init__(self, process_id, all_process_ids):
        super().__init__()
        self.id = process_id
        self.all_process_ids = all_process_ids  # 全プロセスIDのリスト
        self.leader_id = None  # 現在のリーダーID リーダーが決まったら更新

    def keep_listening(self):
        #ソケット通信でデータを受信する
        #データを受信したら別スレッドでhandle_messageを呼び出す
        pass

    def send_message(self, target_port, message):
        #ソケット通信でデータを送信する
        #メッセージにメッセージタイプを付与することで受信側が handle_message() で識別できるようにする
        pass

    def handle_message(self, message):
        #keep_listeningから呼ばれ、受信したメッセージを処理する
        #メッセージタイプに応じて別の処理を行う
        pass

    def run(self):
        print(f"[Process {self.id}] 起動しました。")
        #個別スレッドとしてソケット通信を待つkeep_listeningを起動
        listener_thread = threading.Thread(target=self.keep_listening)
        listener_thread.daemon = True
        listener_thread.start()

        while True:
            # 定期的にリーダーの存在を確認し、必要に応じて選挙を開始する
            pass 

if __name__ == "__main__":
    # 簡単なテストのためにプロセスIDをいくつか定義
    process_ids = [10001, 10002, 10003]

    # ユーザーにどのプロセスを起動するか選ばせる
    #0なら10001、1なら10002、2なら10003を起動という具合
    index = input("Enter index (0, 1, or 2) to kill corresponding process after start: ")
    index = int(index) if index.isdigit() else None
    p = Process(process_ids[index], process_ids) 
    p.run()