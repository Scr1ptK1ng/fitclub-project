import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 5,
  duration: "20s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
  },
};

const baseUrl = __ENV.BASE_URL || "http://host.docker.internal:5000";

export default function () {
  const response = http.get(`${baseUrl}/health`);
  check(response, {
    "health returns 200": (item) => item.status === 200,
    "health reports database ok": (item) => item.json("database") === "ok",
  });
  sleep(0.2);
}
