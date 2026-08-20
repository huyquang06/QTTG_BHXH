package com.qttg.qttg_backend.repository;

import com.qttg.qttg_backend.model.QttgBhxhDetail;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface QttgBhxhDetailRepository extends JpaRepository<QttgBhxhDetail, Long> {
    // Interface này tạm thời để trống, sau này cần các thao tác ghi/xóa/sửa trực tiếp trên bảng Detail
}