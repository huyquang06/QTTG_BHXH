package com.qttg.qttg_backend.config;

    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.context.annotation.Configuration;
    import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
    import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

    @Configuration
    public class WebConfig implements WebMvcConfigurer {

        @Autowired
        private RequestLoggingInterceptor loggingInterceptor;

        @Override
        public void addInterceptors(InterceptorRegistry registry) {
            // Chỉ cấu hình ghi log với các request gọi vào đường dẫn /api/v1/...
            registry.addInterceptor(loggingInterceptor)
                    .addPathPatterns("/api/v1/**");
        }
    }