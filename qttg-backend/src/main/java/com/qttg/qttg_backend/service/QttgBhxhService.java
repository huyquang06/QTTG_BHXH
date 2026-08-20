package com.qttg.qttg_backend.service;

import com.qttg.qttg_backend.dto.DetailDto;
import com.qttg.qttg_backend.dto.PageData;
import com.qttg.qttg_backend.dto.SearchResponse;
import com.qttg.qttg_backend.dto.UserDto;
import com.qttg.qttg_backend.model.QttgBhxh;
import com.qttg.qttg_backend.model.QttgBhxhDetail;
import com.qttg.qttg_backend.repository.QttgBhxhRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.YearMonth;
import java.util.Collections;
import java.util.List;

@Service
@RequiredArgsConstructor
public class QttgBhxhService {

    private final QttgBhxhRepository qttgBhxhRepository;

    @Transactional(readOnly = true)
    public SearchResponse<UserDto> searchUsers(String keyword, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        String searchKey = keyword == null ? "" : keyword.trim();

        Page<QttgBhxh> pageResult = qttgBhxhRepository.searchByKeyword(searchKey, pageable);

        List<UserDto> userDtos = pageResult.getContent().stream()
                .map(this::convertToUserDto)
                .toList();

        PageData<UserDto> pageData = PageData.<UserDto>builder()
                .content(userDtos)
                .pageNo(pageResult.getNumber())
                .pageSize(pageResult.getSize())
                .totalElements(pageResult.getTotalElements())
                .totalPages(pageResult.getTotalPages())
                .build();

        return SearchResponse.<UserDto>builder()
                .status(200)
                .message("Thành công")
                .data(pageData)
                .build();
    }

    private UserDto convertToUserDto(QttgBhxh master) {
        List<DetailDto> detailDtos = safeDetails(master).stream()
                .map(this::convertToDetailDto)
                .toList();

        return UserDto.builder()
                .key(master.getSoSoBhxh())
                .fullName(master.getFullName())
                .details(detailDtos)
                .build();
    }

    private DetailDto convertToDetailDto(QttgBhxhDetail detail) {
        return DetailDto.builder()
                .company(detail.getTenDonVi())
                .fromDate(formatMonth(detail.getTuThang()))
                .toDate(formatEndMonth(detail.getDenThang()))
                .build();
    }

    private List<QttgBhxhDetail> safeDetails(QttgBhxh master) {
        if (master.getDetails() == null) {
            return Collections.emptyList();
        }
        return master.getDetails();
    }

    private String formatMonth(String yyyymm) {
        if (yyyymm == null || yyyymm.length() != 6) {
            return yyyymm;
        }
        return yyyymm.substring(4, 6) + "/" + yyyymm.substring(0, 4);
    }

    private String formatEndMonth(String yyyymm) {
        if (yyyymm == null || yyyymm.length() != 6) {
            return yyyymm;
        }

        try {
            int year = Integer.parseInt(yyyymm.substring(0, 4));
            int month = Integer.parseInt(yyyymm.substring(4, 6));
            YearMonth endMonth = YearMonth.of(year, month);

            if (!endMonth.isBefore(YearMonth.now())) {
                return "Nay";
            }
            return String.format("%02d/%d", month, year);
        } catch (RuntimeException e) {
            return yyyymm;
        }
    }
}
