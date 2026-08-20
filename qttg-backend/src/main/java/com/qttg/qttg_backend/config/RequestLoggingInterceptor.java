package com.qttg.qttg_backend.config;

    import jakarta.servlet.http.HttpServletRequest;
    import jakarta.servlet.http.HttpServletResponse;
    import lombok.extern.slf4j.Slf4j;
    import org.springframework.stereotype.Component;
    import org.springframework.web.servlet.HandlerInterceptor;

    @Component
    @Slf4j
    public class RequestLoggingInterceptor implements HandlerInterceptor {

        @Override
        public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
            String uri = request.getRequestURI();
            String method = request.getMethod();
            String queryString = request.getQueryString();

            // Log lại thông tin đầu vào của request gọi tới API
            log.info("[API REQUEST] Method: {} | URL: {} | Params: {}",
                    method, uri, (queryString != null ? queryString : "None"));
            return true;
        }

        @Override
        public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
            if (ex != null) {
                log.error("[API RESPONSE ERROR] URL: {} | Failed with exception: ", request.getRequestURI(), ex);
            } else {
                log.info("[API RESPONSE] URL: {} | Status: {}", request.getRequestURI(), response.getStatus());
            }
        }
    }