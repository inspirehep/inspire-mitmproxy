FROM mitmproxy/mitmproxy:3.0.3
COPY ./ /code
COPY ./mitmproxy-ca.pem /home/mitmproxy/.mitmproxy/mitmproxy-ca.pem
EXPOSE 8081 8081
CMD mitmweb -s /code/entrypoint.py --web-iface 0.0.0.0
