import socket
import mysql.connector

# DNS 서버 정보
dns_host = '192.168.0.32'  # DNS 서버 IP 주소
dns_port = 1234        # DNS 서버 포트 번호

# 데이터베이스 연결
try:
    # MySQL 연결 설정
    mysql_connection = mysql.connector.connect(
        host="localhost",    # 데이터베이스 호스트
        user="root",          # 데이터베이스 사용자
        password="0000",     # 사용자 비밀번호
        db="socket"          # 사용할 데이터베이스 이름
    )
    print("데이터베이스 연결 성공")
except mysql.connector.Error as e:
    print("데이터베이스 연결 오류:", str(e))  # 연결 실패 시 오류 메시지 출력

def create_dns_table():
    # MySQL 커서 객체 생성
    cursor = mysql_connection.cursor()
    # DNS 정보를 저장할 테이블 생성. 이미 존재할 경우 넘어감.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS domain_ip (
            id INT AUTO_INCREMENT PRIMARY KEY,  # 기본키
            domain VARCHAR(255) NOT NULL,       # 도메인 이름
            ip_address VARCHAR(45) NOT NULL    # IP 주소
        )
    """)
    mysql_connection.commit()  # 변경사항 커밋
    cursor.close()  # 커서 객체 종료

def handle_dns_query(connection, client_address):
    # 클라이언트로부터 데이터 수신
    data = connection.recv(1024)
    # 수신된 데이터를 쿼리 타입과 쿼리 내용으로 분리
    query_type, query_content = data.decode().split(maxsplit=1)
    print(query_type)
    print(query_content)

    if query_type == 'N':
        # 도메인 이름을 이용해 데이터베이스에서 IP 주소를 찾음
        cursor = mysql_connection.cursor()
        query = "SELECT ip_address FROM domain_ip WHERE domain = %s"
        values = (query_content,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        cursor.close()

        if result is not None:
            ip_address = result[0]
        else:
            ip_address = "해당 도메인의 IP 주소를 찾을 수 없습니다."
        response = ip_address

    elif query_type == 'R':
        # IP 주소를 이용해 데이터베이스에서 도메인 이름을 찾음
        cursor = mysql_connection.cursor()
        query = "SELECT domain FROM domain_ip WHERE ip_address = %s"
        values = (query_content,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        cursor.close()

        if result is not None:
            domain = result[0]
        else:
            domain = "해당 IP의 도메인을 찾을 수 없습니다."
        response = domain

    elif query_type == 'W':
        # 쿼리 내용을 도메인 이름과 IP 주소로 분리
        domain, ip_address = query_content.split()
        # 데이터베이스에 도메인 이름과 IP 주소를 등록
        cursor = mysql_connection.cursor()
        query = "INSERT INTO domain_ip (domain, ip_address) VALUES (%s, %s)"
        values = (domain, ip_address)
        try:
            cursor.execute(query, values)
            if cursor.rowcount == 1:
                mysql_connection.commit()
                print("데이터베이스에 등록 완료")
                response = f"{domain} 도메인이 {ip_address} IP 주소와 함께 등록되었습니다."
            else:
                print("데이터베이스 등록 실패")
                response = "도메인 등록 중 오류가 발생했습니다."
        except Exception as e:
            error_message = f"도메인 등록 중 오류가 발생했습니다: {str(e)}"
            print(error_message)  # 서버의 콘솔에 에러 메시지 출력
            response = error_message
        finally:
            cursor.close()

    else:
        response = "잘못된 쿼리 유형을 받았습니다."
    
    # 응답 전송
    connection.send(response.encode())
    connection.close()
    return

# 소켓 생성 및 바인드, 리스닝
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((dns_host, dns_port))
server_socket.listen(1)

# 데이터베이스에 테이블 생성
create_dns_table()

while True:
    # 클라이언트 연결 수락
    connection, client_address = server_socket.accept()
    print("클라이언트와 연결되었습니다.")
    # DNS 쿼리 처리
    handle_dns_query(connection, client_address)

# 소켓 종료
server_socket.close()
