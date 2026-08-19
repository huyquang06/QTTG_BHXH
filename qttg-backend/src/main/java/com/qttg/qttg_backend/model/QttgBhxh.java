package com.qttg.qttg_backend.model;

    import com.fasterxml.jackson.annotation.JsonManagedReference;
    import jakarta.persistence.*;
    import lombok.Getter;
    import lombok.Setter;
    import lombok.NoArgsConstructor;
    import lombok.AllArgsConstructor;

    import java.time.LocalDateTime;
    import java.util.List;

    @Entity
    @Table(name = "qttg_bhxh")
    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public class QttgBhxh {

        @Id
        private Long id; // Không dùng @GeneratedValue vì ID đã được sinh sẵn từ file Parquet (qua Spark Job)

        @Column(name = "nld_id", nullable = false)
        private Long nldId;

        @Column(name = "so_so_bhxh", nullable = false, unique = true, length = 20)
        private String soSoBhxh;

        @Column(name = "full_name", length = 150)
        private String fullName;

        @Column(name = "thang_bd", length = 6)
        private String thangBd;

        @Column(name = "thang_kt", length = 6)
        private String thangKt;

        // insertable = false, updatable = false để tránh Hibernate cố ghi đè trường này (để DB tự điền default)
        @Column(name = "created_at", insertable = false, updatable = false)
        private LocalDateTime createdAt;

        @Column(name = "updated_at", insertable = false, updatable = false)
        private LocalDateTime updatedAt;

        // Thiết lập quan hệ 1-N tới bảng Detail
        // mappedBy = "master" liên kết tới thuộc tính "master" trong lớp QttgBhxhDetail
        // FetchType.LAZY để chỉ khi cần thiết mới truy vấn bảng Detail, tránh tải nặng DB
        @OneToMany(mappedBy = "master", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
        @JsonManagedReference // Quản lý serialize JSON từ cha xuống con
        private List<QttgBhxhDetail> details;
    }