package com.qttg.qttg_backend.exception;

import com.qttg.qttg_backend.dto.SearchResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

@RestControllerAdvice
@Slf4j // Tự động tích hợp Logback/SLF4J của Spring Boot thông qua Lombok
public class GlobalExceptionHandler {

        // Bắt lỗi 1: Khi người dùng truyền tham số sai kiểu dữ liệu (Ví dụ: truyền page=abc)
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<SearchResponse<Object>> handleTypeMismatch(MethodArgumentTypeMismatchException ex) {
        String message = String.format("Tham số '%s' truyền sai kiểu dữ liệu. Yêu cầu kiểu: %s",
                ex.getName(), ex.getRequiredType().getSimpleName());

        log.error("[API ERROR] Lỗi kiểu dữ liệu tham số: {}", message);

        SearchResponse<Object> response = SearchResponse.builder()
                .status(HttpStatus.BAD_REQUEST.value())
                .message(message)
                .data(null)
                .build();

        return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
    }

        // Bắt lỗi 2: Lỗi truyền đối số không hợp lệ trong code
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<SearchResponse<Object>> handleIllegalArgument(IllegalArgumentException ex) {
        log.error("[API ERROR] Lỗi đối số không hợp lệ: {}", ex.getMessage());

        SearchResponse<Object> response = SearchResponse.builder()
                .status(HttpStatus.BAD_REQUEST.value())
                .message(ex.getMessage())
                .data(null)
                .build();

        return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
    }

        // Bắt lỗi 3: Bắt mọi Exception không xác định khác (Lỗi hệ thống 500)
    @ExceptionHandler(Exception.class)
    public ResponseEntity<SearchResponse<Object>> handleGeneralException(Exception ex) {
            // Ghi lại đầy đủ Stacktrace ra console/file để lập trình viên dễ debug lỗi
        log.error("[CRITICAL ERROR] Lỗi hệ thống nghiêm trọng: ", ex);

        SearchResponse<Object> response = SearchResponse.builder()
                .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                .message("Đã xảy ra lỗi hệ thống nghiêm trọng. Vui lòng liên hệ quản trị viên!")
                .data(null)
                .build();

        return new ResponseEntity<>(response, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}