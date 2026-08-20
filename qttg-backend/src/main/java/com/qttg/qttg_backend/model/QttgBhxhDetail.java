package com.qttg.qttg_backend.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "qttg_bhxh_detail")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class QttgBhxhDetail {

    @Id
    private Long id;

    // Nhiều dòng Detail thuộc về 1 dòng Master
    // JoinColumn khai báo khóa ngoại "master_id" ở bảng Detail liên kết sang khóa chính "id" ở bảng Master
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "master_id", nullable = false)
    @JsonBackReference // Chặn việc serialize ngược từ con lên cha để tránh lặp vô hạn (Circular Reference)
    private QttgBhxh master;

    @Column(name = "nld_id", nullable = false)
    private Long nldId;

    @Column(name = "tu_thang", nullable = false, length = 6)
    private String tuThang;

    @Column(name = "den_thang", nullable = false, length = 6)
    private String denThang;

    @Column(name = "ma_don_vi", length = 50)
    private String maDonVi;

    @Column(name = "ten_don_vi", length = 255)
    private String tenDonVi;

    // Numeric(19,4) trong DB tương ứng kiểu BigDecimal trong Java để đảm bảo độ chính xác số học
    @Column(name = "muc_luong", precision = 19, scale = 4)
    private BigDecimal mucLuong;

    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;
}