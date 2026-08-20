package com.qttg.qttg_backend.controller;

import com.qttg.qttg_backend.dto.SearchResponse;
import com.qttg.qttg_backend.dto.UserDto;
import com.qttg.qttg_backend.service.QttgBhxhService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/users")
public class QttgBhxhController {

    @Autowired
    private QttgBhxhService qttgBhxhService;

    @GetMapping("/search")
    public SearchResponse<UserDto> search(
            @RequestParam(value = "keyword", required = false, defaultValue = "") String keyword,
            @RequestParam(value = "page", required = false, defaultValue = "0") int page,
            @RequestParam(value = "size", required = false, defaultValue = "10") int size) {
        return qttgBhxhService.searchUsers(keyword, page, size);
    }
}