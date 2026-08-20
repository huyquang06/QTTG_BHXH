package com.qttg.qttg_backend.repository;

import com.qttg.qttg_backend.model.QttgBhxh;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface QttgBhxhRepository extends JpaRepository<QttgBhxh, Long> {

    // JPQL truy vấn tìm kiếm phân trang. Hỗ trợ tìm theo Số sổ BHXH hoặc tìm không phân biệt hoa thường theo Tên.
    @Query("SELECT q FROM QttgBhxh q WHERE q.soSoBhxh LIKE %:keyword% OR LOWER(q.fullName) LIKE LOWER(CONCAT('%', :keyword, '%'))")
    Page<QttgBhxh> searchByKeyword(@Param("keyword") String keyword, Pageable pageable);
}