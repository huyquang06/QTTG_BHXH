package com.qttg.qttg_backend;

import java.util.TimeZone;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class QttgBackendApplication {

	public static void main(String[] args) {
		 TimeZone.setDefault(TimeZone.getTimeZone("Asia/Ho_Chi_Minh"));

        SpringApplication.run(QttgBackendApplication.class, args);
	}

}
