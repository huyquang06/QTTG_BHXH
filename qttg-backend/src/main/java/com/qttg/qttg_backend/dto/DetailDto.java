// Đại diện cho 1 dòng chi tiết quá trình tham gia BHXH
package com.qttg.qttg_backend.dto;

    import lombok.AllArgsConstructor;
    import lombok.Builder;
    import lombok.Data;
    import lombok.NoArgsConstructor;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public class DetailDto {
        private String company;
        private String fromDate;
        private String toDate;
    }