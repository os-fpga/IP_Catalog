#ifndef __SPI_FLASH_CSR_H
#define __SPI_FLASH_CSR_H
#include <stdint.h>
#include <system.h>
#ifndef CSR_ACCESSORS_DEFINED
#include <hw/common.h>
#endif /* ! CSR_ACCESSORS_DEFINED */
#define SPI_FLASH_CSR_BASE 0x81000000L

/* spiflash_core */
#define CSR_SPIFLASH_CORE_BASE (SPI_FLASH_CSR_BASE + 0x800L)
#define CSR_SPIFLASH_CORE_MASTER_CS_ADDR (SPI_FLASH_CSR_BASE + 0x800L)
#define CSR_SPIFLASH_CORE_MASTER_CS_SIZE 1
static inline uint32_t spiflash_core_master_cs_read(void) {
	return csr_read_simple((SPI_FLASH_CSR_BASE + 0x800L));
}
static inline void spiflash_core_master_cs_write(uint32_t v) {
	csr_write_simple(v, (SPI_FLASH_CSR_BASE + 0x800L));
}
#define CSR_SPIFLASH_CORE_MASTER_PHYCONFIG_ADDR (SPI_FLASH_CSR_BASE + 0x804L)
#define CSR_SPIFLASH_CORE_MASTER_PHYCONFIG_SIZE 1
static inline uint32_t spiflash_core_master_phyconfig_read(void) {
	return csr_read_simple((SPI_FLASH_CSR_BASE + 0x804L));
}
static inline void spiflash_core_master_phyconfig_write(uint32_t v) {
	csr_write_simple(v, (SPI_FLASH_CSR_BASE + 0x804L));
}
#define CSR_SPIFLASH_CORE_MASTER_PHYCONFIG_LEN_OFFSET 0
#define CSR_SPIFLASH_CORE_MASTER_PHYCONFIG_LEN_SIZE 8
static inline uint32_t spiflash_core_master_phyconfig_len_extract(uint32_t oldword) {
	uint32_t mask = 0xff;
	return ( (oldword >> 0) & mask );
}
static inline uint32_t spiflash_core_master_phyconfig_len_read(void) {
	uint32_t word = spiflash_core_master_phyconfig_read();
	return spiflash_core_master_phyconfig_len_extract(word);
}
static inline uint32_t spiflash_core_master_phyconfig_len_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = 0xff;
	return (oldword & (~(mask << 0))) | (mask & plain_value)<< 0 ;
}
static inline void spiflash_core_master_phyconfig_len_write(uint32_t plain_value) {
	uint32_t oldword = spiflash_core_master_phyconfig_read();
	uint32_t newword = spiflash_core_master_phyconfig_len_replace(oldword, plain_value);
	spiflash_core_master_phyconfig_write(newword);
}
#define CSR_SPIFLASH_CORE_MASTER_PHYCONFIG_WIDTH_OFFSET 8
#define CSR_SPIFLASH_CORE_MASTER_PHYCONFIG_WIDTH_SIZE 4
static inline uint32_t spiflash_core_master_phyconfig_width_extract(uint32_t oldword) {
	uint32_t mask = 0xf;
	return ( (oldword >> 8) & mask );
}
static inline uint32_t spiflash_core_master_phyconfig_width_read(void) {
	uint32_t word = spiflash_core_master_phyconfig_read();
	return spiflash_core_master_phyconfig_width_extract(word);
}
static inline uint32_t spiflash_core_master_phyconfig_width_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = 0xf;
	return (oldword & (~(mask << 8))) | (mask & plain_value)<< 8 ;
}
static inline void spiflash_core_master_phyconfig_width_write(uint32_t plain_value) {
	uint32_t oldword = spiflash_core_master_phyconfig_read();
	uint32_t newword = spiflash_core_master_phyconfig_width_replace(oldword, plain_value);
	spiflash_core_master_phyconfig_write(newword);
}
#define CSR_SPIFLASH_CORE_MASTER_PHYCONFIG_MASK_OFFSET 16
#define CSR_SPIFLASH_CORE_MASTER_PHYCONFIG_MASK_SIZE 8
static inline uint32_t spiflash_core_master_phyconfig_mask_extract(uint32_t oldword) {
	uint32_t mask = 0xff;
	return ( (oldword >> 16) & mask );
}
static inline uint32_t spiflash_core_master_phyconfig_mask_read(void) {
	uint32_t word = spiflash_core_master_phyconfig_read();
	return spiflash_core_master_phyconfig_mask_extract(word);
}
static inline uint32_t spiflash_core_master_phyconfig_mask_replace(uint32_t oldword, uint32_t plain_value) {
	uint32_t mask = 0xff;
	return (oldword & (~(mask << 16))) | (mask & plain_value)<< 16 ;
}
static inline void spiflash_core_master_phyconfig_mask_write(uint32_t plain_value) {
	uint32_t oldword = spiflash_core_master_phyconfig_read();
	uint32_t newword = spiflash_core_master_phyconfig_mask_replace(oldword, plain_value);
	spiflash_core_master_phyconfig_write(newword);
}
#define CSR_SPIFLASH_CORE_MASTER_RXTX_ADDR (SPI_FLASH_CSR_BASE + 0x808L)
#define CSR_SPIFLASH_CORE_MASTER_RXTX_SIZE 1
static inline uint32_t spiflash_core_master_rxtx_read(void) {
	return csr_read_simple((SPI_FLASH_CSR_BASE + 0x808L));
}
static inline void spiflash_core_master_rxtx_write(uint32_t v) {
	csr_write_simple(v, (SPI_FLASH_CSR_BASE + 0x808L));
}
#define CSR_SPIFLASH_CORE_MASTER_STATUS_ADDR (SPI_FLASH_CSR_BASE + 0x80cL)
#define CSR_SPIFLASH_CORE_MASTER_STATUS_SIZE 1
static inline uint32_t spiflash_core_master_status_read(void) {
	return csr_read_simple((SPI_FLASH_CSR_BASE + 0x80cL));
}
#define CSR_SPIFLASH_CORE_MASTER_STATUS_TX_READY_OFFSET 0
#define CSR_SPIFLASH_CORE_MASTER_STATUS_TX_READY_SIZE 1
static inline uint32_t spiflash_core_master_status_tx_ready_extract(uint32_t oldword) {
	uint32_t mask = 0x1;
	return ( (oldword >> 0) & mask );
}
static inline uint32_t spiflash_core_master_status_tx_ready_read(void) {
	uint32_t word = spiflash_core_master_status_read();
	return spiflash_core_master_status_tx_ready_extract(word);
}
#define CSR_SPIFLASH_CORE_MASTER_STATUS_RX_READY_OFFSET 1
#define CSR_SPIFLASH_CORE_MASTER_STATUS_RX_READY_SIZE 1
static inline uint32_t spiflash_core_master_status_rx_ready_extract(uint32_t oldword) {
	uint32_t mask = 0x1;
	return ( (oldword >> 1) & mask );
}
static inline uint32_t spiflash_core_master_status_rx_ready_read(void) {
	uint32_t word = spiflash_core_master_status_read();
	return spiflash_core_master_status_rx_ready_extract(word);
}

/* spiflash_phy */
#define CSR_SPIFLASH_PHY_BASE (SPI_FLASH_CSR_BASE + 0x1000L)
#define CSR_SPIFLASH_PHY_CLK_DIVISOR_ADDR (SPI_FLASH_CSR_BASE + 0x1000L)
#define CSR_SPIFLASH_PHY_CLK_DIVISOR_SIZE 1
static inline uint32_t spiflash_phy_clk_divisor_read(void) {
	return csr_read_simple((SPI_FLASH_CSR_BASE + 0x1000L));
}
static inline void spiflash_phy_clk_divisor_write(uint32_t v) {
	csr_write_simple(v, (SPI_FLASH_CSR_BASE + 0x1000L));
}

#endif
