import socket

# DNS 서버 정보
dns_host = '192.168.0.32'  # DNS 서버 IP 주소
dns_port = 1234         # DNS 서버 포트 번호

# DNS 서버에 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((dns_host, dns_port))

while True:
    # DNS 쿼리 요청 입력
    option = input("DNS 쿼리를 선택하세요 ('N': 도메인 조회, 'R': IP 주소 조회, 'W': 도메인 등록, 'quit': 종료): ")
    
    if option == 'quit':
        print("프로그램 종료")
        break

    if option == 'N':
        domain = input("도메인 이름을 입력하세요: ")
        query = f"N {domain}"

    elif option == 'R':
        ip_address = input("IP 주소를 입력하세요: ")
        query = f"R {ip_address}"

    elif option == 'W':
        domain = input("등록할 도메인 이름을 입력하세요: ")
        ip_address = input("등록할 IP 주소를 입력하세요: ")
        query = f"W {domain} {ip_address}"

    else:
        print("잘못된 입력입니다. 다시 시도하세요.")
        continue

    # DNS 쿼리 요청 전송
    client_socket.send(query.encode())

    # DNS 응답 수신
    response = client_socket.recv(1024).decode()

    # 응답 출력
    if option == 'N':
        print("해당 도메인의 IP주소: " + response)
    
    elif option == 'R':
        print("해당 IP주소의 도메인: " + response)

    elif option == 'W':
        print("도메인 등록이 완료되었습니다. 등록된 도메인: "+ domain + ", IP주소: " + ip_address)

# 연결 종료
client_socket.close()
